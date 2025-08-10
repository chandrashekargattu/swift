"""
Advanced AI Chatbot Service with RAG, NLP, and Multiple LLM Support
Falls back to lightweight version if dependencies are not available
"""
import os
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Try to import advanced AI/ML dependencies
AI_DEPS_AVAILABLE = True
try:
    # Core AI/ML Libraries
    import numpy as np
    import pandas as pd
    from sklearn.metrics.pairwise import cosine_similarity

    # LangChain Core
    from langchain.schema import Document, BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
    from langchain.chains import ConversationalRetrievalChain, LLMChain
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
    from langchain.callbacks import AsyncIteratorCallbackHandler
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Chroma, FAISS
    from langchain.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    from langchain.tools import Tool
    from langchain.agents import AgentExecutor, create_openai_tools_agent

    # LLM Models
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_anthropic import ChatAnthropic
    from langchain_community.llms import HuggingFaceHub
    from langchain_community.chat_models import ChatGoogleGenerativeAI

    # NLP Libraries
    import spacy
    import nltk
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from sentence_transformers import SentenceTransformer

    # Vector Databases
    import chromadb
    from chromadb.config import Settings
    import faiss

    # Download required NLTK data
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    
except ImportError as e:
    AI_DEPS_AVAILABLE = False
    logger.warning(f"Advanced AI dependencies not available: {e}")
    logger.info("Falling back to lightweight chatbot service")

# Additional utilities
from app.core.config import settings
from app.core.database import db

# Import lightweight version as fallback
from app.services.ai_chatbot_lite import LightweightAIChatbotService, AIProvider

# Define the service based on available dependencies
if AI_DEPS_AVAILABLE:
    class AdvancedAIChatbotService:
        def __init__(self):
            self.db = db
            
            # Initialize NLP models
            self._init_nlp_models()
            
            # Initialize Vector Store
            self._init_vector_store()
            
            # Initialize LLMs
            self._init_llms()
            
            # Initialize conversation memory
            self.conversations = {}
            
            # Initialize tools for agent
            self._init_tools()
            
            # Load knowledge base
            asyncio.create_task(self._load_knowledge_base())
        
        def _init_nlp_models(self):
            """Initialize NLP models for advanced understanding"""
            try:
                # SpaCy for entity recognition
                self.nlp = spacy.load("en_core_web_sm")
            except:
                logger.warning("SpaCy model not found, downloading...")
                os.system("python -m spacy download en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
        
        # Sentiment Analysis
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        # Intent Classification
        self.intent_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Sentence Embeddings for semantic search
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Emotion Detection
        self.emotion_detector = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None
        )
        
    def _init_vector_store(self):
        """Initialize vector database for RAG"""
        # Using HuggingFace embeddings for cost efficiency
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # Create collections
        self.knowledge_collection = self.chroma_client.get_or_create_collection(
            name="rideswift_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.conversation_collection = self.chroma_client.get_or_create_collection(
            name="conversation_history",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize FAISS for fast similarity search
        self.faiss_index = None
        self.faiss_documents = []
        
    def _init_llms(self):
        """Initialize multiple LLM providers"""
        self.llm_providers = {}
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.llm_providers[AIProvider.OPENAI] = ChatOpenAI(
                model_name="gpt-4-turbo-preview",
                temperature=0.7,
                max_tokens=1000,
                streaming=True
            )
        
        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            self.llm_providers[AIProvider.ANTHROPIC] = ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=0.7,
                max_tokens=1000
            )
        
        # Google
        if os.getenv("GOOGLE_API_KEY"):
            self.llm_providers[AIProvider.GOOGLE] = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                temperature=0.7,
                max_output_tokens=1000
            )
        
        # Default to OpenAI or first available
        self.default_llm = self.llm_providers.get(
            AIProvider.OPENAI,
            next(iter(self.llm_providers.values())) if self.llm_providers else None
        )
        
    def _init_tools(self):
        """Initialize tools for the AI agent"""
        self.tools = [
            Tool(
                name="search_bookings",
                func=self._search_bookings_tool,
                description="Search for user bookings by status, date, or route"
            ),
            Tool(
                name="calculate_fare",
                func=self._calculate_fare_tool,
                description="Calculate fare for a given route and vehicle type"
            ),
            Tool(
                name="check_availability",
                func=self._check_availability_tool,
                description="Check vehicle availability for a specific date and route"
            ),
            Tool(
                name="get_weather",
                func=self._get_weather_tool,
                description="Get weather information for travel planning"
            ),
            Tool(
                name="search_knowledge",
                func=self._search_knowledge_tool,
                description="Search internal knowledge base for policies and information"
            )
        ]
        
    async def _load_knowledge_base(self):
        """Load company knowledge into vector store"""
        knowledge_docs = [
            # Company Policies
            {
                "content": "RideSwift Cancellation Policy: Free cancellation up to 6 hours before pickup. 50% charge for cancellations between 2-6 hours. Full charge for less than 2 hours or no-show.",
                "metadata": {"category": "policy", "topic": "cancellation"}
            },
            {
                "content": "RideSwift Safety Policy: All drivers undergo background checks. Vehicles are sanitized after each ride. GPS tracking available. Emergency button in app. 24/7 support hotline.",
                "metadata": {"category": "policy", "topic": "safety"}
            },
            {
                "content": "RideSwift Pricing: Sedan ₹12/km, SUV ₹16/km, Luxury ₹25/km, Tempo ₹22/km. Toll charges included. No hidden fees. GST included in price.",
                "metadata": {"category": "pricing", "topic": "rates"}
            },
            {
                "content": "RideSwift Fleet: Sedan (4 seaters) - Swift Dzire, Honda City. SUV (6 seaters) - Innova, Ertiga. Luxury (4 seaters) - Mercedes, BMW. Tempo (12 seaters) - Force Traveller.",
                "metadata": {"category": "fleet", "topic": "vehicles"}
            },
            {
                "content": "Popular Routes: Hyderabad-Bangalore (570km, 8hrs), Hyderabad-Chennai (520km, 8hrs), Delhi-Jaipur (280km, 5hrs), Mumbai-Pune (150km, 3hrs).",
                "metadata": {"category": "routes", "topic": "popular"}
            },
            {
                "content": "Booking Process: 1. Select route and date 2. Choose vehicle type 3. Enter passenger details 4. Review and confirm 5. Receive booking confirmation 6. Driver details sent 2 hours before pickup.",
                "metadata": {"category": "process", "topic": "booking"}
            },
            {
                "content": "Payment Options: Credit/Debit cards, Net banking, UPI, Digital wallets. Partial payment option available. Corporate billing available.",
                "metadata": {"category": "payment", "topic": "methods"}
            },
            {
                "content": "Driver Standards: Professional licensed drivers. Minimum 5 years experience. Trained in customer service. Wear uniforms. Speak multiple languages. COVID vaccinated.",
                "metadata": {"category": "quality", "topic": "drivers"}
            }
        ]
        
        # Add to vector store
        for doc in knowledge_docs:
            embedding = self.embeddings.embed_query(doc["content"])
            self.knowledge_collection.add(
                embeddings=[embedding],
                documents=[doc["content"]],
                metadatas=[doc["metadata"]],
                ids=[f"knowledge_{knowledge_docs.index(doc)}"]
            )
        
        logger.info("Knowledge base loaded successfully")
        
    def _create_chat_prompt(self) -> ChatPromptTemplate:
        """Create the main chat prompt template"""
        system_template = """You are Swift AI, an advanced AI assistant for RideSwift interstate cab booking service.
        
Your personality:
- Empathetic and understanding
- Professional yet friendly
- Proactive in offering help
- Culturally aware (Indian context)
- Safety-conscious

Your capabilities:
- Book interstate cabs
- Provide real-time fare calculations
- Check availability
- Answer policy questions
- Handle complaints with empathy
- Provide travel recommendations
- Multiple language support (focus on English, Hindi)

Current context:
- User: {user_name}
- Previous bookings: {booking_count}
- Preferred vehicle: {preferred_vehicle}
- Current time: {current_time}
- User emotion: {emotion}

Conversation history is provided for context.

Always:
1. Address the user by name when known
2. Show empathy based on their emotional state
3. Provide specific, actionable help
4. Use relevant emojis appropriately
5. Offer quick action suggestions
6. Ensure safety and comfort
7. Be concise but thorough

Retrieved Context:
{context}

Remember: You're not just a booking assistant, you're a travel companion who ensures safe, comfortable journeys."""
        
        human_template = "{input}"
        
        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder("chat_history"),
            ("human", human_template)
        ])
        
    async def get_user_context(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Get comprehensive user context"""
        if not user_id:
            return {
                "user_name": "valued customer",
                "booking_count": 0,
                "preferred_vehicle": None,
                "recent_routes": [],
                "emotion_history": []
            }
        
        try:
            # Get user details
            user_data = await self.db.db.users.find_one({"_id": user_id})
            
            # Get booking history
            bookings = await self.db.db.bookings.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(10).to_list(10)
            
            # Analyze preferences
            vehicle_counts = {}
            routes = []
            for booking in bookings:
                vehicle = booking.get("cab_type", "sedan")
                vehicle_counts[vehicle] = vehicle_counts.get(vehicle, 0) + 1
                routes.append({
                    "from": booking.get("pickup_location", {}).get("city"),
                    "to": booking.get("drop_location", {}).get("city")
                })
            
            preferred_vehicle = max(vehicle_counts, key=vehicle_counts.get) if vehicle_counts else None
            
            return {
                "user_name": user_data.get("full_name", "valued customer").split()[0],
                "booking_count": len(bookings),
                "preferred_vehicle": preferred_vehicle,
                "recent_routes": routes[:3],
                "last_booking": bookings[0] if bookings else None,
                "user_since": user_data.get("created_at"),
                "is_premium": len(bookings) > 5
            }
        except Exception as e:
            logger.error(f"Error fetching user context: {e}")
            return {
                "user_name": "valued customer",
                "booking_count": 0,
                "preferred_vehicle": None,
                "recent_routes": []
            }
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """Comprehensive message analysis using NLP"""
        # SpaCy NER
        doc = self.nlp(message)
        entities = {
            "locations": [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]],
            "dates": [ent.text for ent in doc.ents if ent.label_ == "DATE"],
            "times": [ent.text for ent in doc.ents if ent.label_ == "TIME"],
            "persons": [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
            "money": [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
        }
        
        # Intent Classification
        intents = self.intent_classifier(
            message,
            candidate_labels=[
                "booking_request", "price_inquiry", "cancellation",
                "complaint", "status_check", "general_question",
                "greeting", "thanks", "help_request", "modification"
            ]
        )
        
        # Sentiment Analysis
        sentiment = self.sentiment_analyzer(message)[0]
        
        # Emotion Detection
        emotions = self.emotion_detector(message)[0]
        primary_emotion = max(emotions, key=lambda x: x['score'])
        
        # Extract route if present
        route = None
        if len(entities["locations"]) >= 2:
            route = {
                "from": entities["locations"][0],
                "to": entities["locations"][1]
            }
        
        return {
            "entities": entities,
            "intent": intents["labels"][0],
            "intent_confidence": intents["scores"][0],
            "sentiment": sentiment["label"],
            "sentiment_score": sentiment["score"],
            "emotion": primary_emotion["label"],
            "emotion_score": primary_emotion["score"],
            "route": route,
            "has_urgency": any(word in message.lower() for word in ["urgent", "asap", "emergency", "immediately"]),
            "has_complaint": any(word in message.lower() for word in ["complaint", "problem", "issue", "bad", "terrible"])
        }
    
    async def search_similar_conversations(self, message: str, user_id: str, limit: int = 3):
        """Search for similar past conversations using vector similarity"""
        embedding = self.embeddings.embed_query(message)
        
        # Search in conversation history
        results = self.conversation_collection.query(
            query_embeddings=[embedding],
            n_results=limit,
            where={"user_id": user_id}
        )
        
        return results
    
    async def generate_response(
        self,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        llm_provider: AIProvider = AIProvider.OPENAI
    ) -> Dict[str, Any]:
        """Generate AI response using RAG and advanced NLP"""
        
        # Get or create session
        if not session_id:
            session_id = f"session_{datetime.now().timestamp()}"
        
        # Analyze message
        analysis = self.analyze_message(message)
        
        # Get user context
        user_context = await self.get_user_context(user_id)
        
        # Search relevant knowledge
        knowledge_results = await self._search_knowledge_tool(message)
        
        # Get conversation memory
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationBufferWindowMemory(
                k=10,
                return_messages=True,
                memory_key="chat_history"
            )
        
        memory = self.conversations[session_id]
        
        # Select LLM
        llm = self.llm_providers.get(llm_provider, self.default_llm)
        if not llm:
            return {
                "response": "I apologize, but I'm having technical difficulties. Please try again or call our support at +91 8143243584.",
                "error": "No LLM available"
            }
        
        # Create prompt
        prompt = self._create_chat_prompt()
        
        # Create chain with RAG
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            memory=memory,
            verbose=True
        )
        
        # Prepare context
        context = {
            "user_name": user_context["user_name"],
            "booking_count": user_context["booking_count"],
            "preferred_vehicle": user_context["preferred_vehicle"] or "not set",
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "emotion": analysis["emotion"],
            "context": knowledge_results,
            "input": message
        }
        
        try:
            # Generate response
            response = await chain.ainvoke(context)
            
            # Store conversation in vector DB
            conv_embedding = self.embeddings.embed_query(f"User: {message}\nAI: {response['text']}")
            self.conversation_collection.add(
                embeddings=[conv_embedding],
                documents=[f"User: {message}\nAI: {response['text']}"],
                metadatas=[{
                    "user_id": user_id or "anonymous",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "intent": analysis["intent"],
                    "emotion": analysis["emotion"]
                }],
                ids=[f"conv_{session_id}_{datetime.now().timestamp()}"]
            )
            
            # Generate suggestions based on context
            suggestions = self._generate_suggestions(analysis, user_context)
            
            # Prepare actions if needed
            actions = self._prepare_actions(analysis, message)
            
            return {
                "response": response["text"],
                "metadata": {
                    "intent": analysis["intent"],
                    "confidence": analysis["intent_confidence"],
                    "emotion": analysis["emotion"],
                    "sentiment": analysis["sentiment"],
                    "entities": analysis["entities"],
                    "route": analysis["route"],
                    "suggestions": suggestions,
                    "actions": actions,
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            
            # Fallback to rule-based response
            fallback_response = self._generate_fallback_response(analysis, user_context)
            return {
                "response": fallback_response,
                "metadata": {
                    "intent": analysis["intent"],
                    "emotion": analysis["emotion"],
                    "error": str(e),
                    "fallback": True
                }
            }
    
    def _generate_suggestions(self, analysis: Dict, user_context: Dict) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []
        
        intent = analysis["intent"]
        
        if intent == "booking_request":
            if analysis["route"]:
                suggestions = [
                    "Check availability",
                    "View fare estimate",
                    "Book for tomorrow",
                    "Round trip option"
                ]
            else:
                suggestions = [
                    "Hyderabad to Bangalore",
                    "Delhi to Jaipur",
                    "Enter custom route",
                    "View popular routes"
                ]
        
        elif intent == "price_inquiry":
            suggestions = [
                "Calculate for my route",
                "Compare vehicle types",
                "View all prices",
                "Get quote"
            ]
        
        elif intent == "complaint":
            suggestions = [
                "Talk to supervisor",
                "File formal complaint",
                "Get immediate help",
                "Request callback"
            ]
        
        elif intent == "status_check":
            suggestions = [
                "Track live location",
                "Contact driver",
                "View booking details",
                "Modify booking"
            ]
        
        else:
            # Default suggestions based on user history
            if user_context["booking_count"] > 0:
                suggestions = [
                    "Book another ride",
                    "View my bookings",
                    "Repeat last booking",
                    "Help center"
                ]
            else:
                suggestions = [
                    "Book first ride",
                    "View pricing",
                    "How it works",
                    "Contact support"
                ]
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def _prepare_actions(self, analysis: Dict, message: str) -> Optional[Dict]:
        """Prepare actionable responses"""
        if analysis["intent"] == "booking_request" and analysis["route"]:
            return {
                "type": "start_booking",
                "data": {
                    "from": analysis["route"]["from"],
                    "to": analysis["route"]["to"],
                    "date": analysis["entities"]["dates"][0] if analysis["entities"]["dates"] else None
                }
            }
        
        elif analysis["has_urgency"] and analysis["has_complaint"]:
            return {
                "type": "escalate_support",
                "data": {
                    "priority": "high",
                    "reason": "urgent_complaint",
                    "sentiment": analysis["sentiment"]
                }
            }
        
        return None
    
    def _generate_fallback_response(self, analysis: Dict, user_context: Dict) -> str:
        """Generate fallback response when LLM fails"""
        intent = analysis["intent"]
        emotion = analysis["emotion"]
        name = user_context["user_name"]
        
        # Empathetic prefix based on emotion
        prefix = ""
        if emotion == "anger":
            prefix = f"I understand you're frustrated, {name}. "
        elif emotion == "sadness":
            prefix = f"I'm sorry you're having a difficult time, {name}. "
        elif emotion == "fear" or analysis["has_urgency"]:
            prefix = f"I understand this is urgent, {name}. "
        elif emotion == "joy":
            prefix = f"Great to hear from you, {name}! "
        
        # Intent-based response
        if intent == "booking_request":
            return prefix + "I'd be happy to help you book a ride! Please tell me your pickup and drop locations, along with your preferred travel date."
        
        elif intent == "price_inquiry":
            return prefix + "Our transparent pricing: Sedan ₹12/km, SUV ₹16/km, Luxury ₹25/km, Tempo ₹22/km. Would you like me to calculate the fare for a specific route?"
        
        elif intent == "complaint":
            return prefix + "I sincerely apologize for any inconvenience. Your concern is important to us. For immediate assistance, please call +91 8143243584 or let me know how I can help resolve this."
        
        elif intent == "status_check":
            return prefix + "I'll help you check your booking status. You can view all bookings in 'My Bookings' section or provide me with your booking ID for quick access."
        
        else:
            return prefix + "I'm here to assist you with bookings, pricing, or any questions about RideSwift. How can I help you today?"
    
    # Tool implementations
    async def _search_bookings_tool(self, query: str) -> str:
        """Search bookings tool"""
        # Implementation for searching bookings
        return "Searching for bookings..."
    
    async def _calculate_fare_tool(self, query: str) -> str:
        """Calculate fare tool"""
        # Parse route from query
        # Calculate based on distance and vehicle type
        return "Calculating fare..."
    
    async def _check_availability_tool(self, query: str) -> str:
        """Check availability tool"""
        return "Checking availability..."
    
    async def _get_weather_tool(self, query: str) -> str:
        """Get weather information"""
        return "Weather information..."
    
    async def _search_knowledge_tool(self, query: str) -> str:
        """Search knowledge base"""
        embedding = self.embeddings.embed_query(query)
        
        results = self.knowledge_collection.query(
            query_embeddings=[embedding],
            n_results=3
        )
        
        if results["documents"]:
            return "\n".join(results["documents"][0])
        return ""
    
    async def train_on_feedback(self, message_id: str, feedback: str, user_id: str):
        """Learn from user feedback to improve responses"""
        # Store feedback for future training
        # This can be used to fine-tune models or adjust response strategies
        pass

else:
    # If dependencies are not available, use the lightweight service
    AdvancedAIChatbotService = LightweightAIChatbotService

# Create singleton instance
ai_chatbot_service = AdvancedAIChatbotService()
