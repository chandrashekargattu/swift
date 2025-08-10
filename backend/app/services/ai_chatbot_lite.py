"""
Lightweight AI Chatbot Service - Works without heavy ML dependencies
Falls back to rule-based responses when AI models are not available
"""
import os
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import logging
import re

from app.core.config import settings
from app.core.database import db

logger = logging.getLogger(__name__)

# Try to import AI dependencies, but don't fail if they're not available
try:
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.schema import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available - using fallback conversation memory")

try:
    import openai
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    FALLBACK = "fallback"

class LightweightAIChatbotService:
    def __init__(self):
        self.db = db
        self.conversations = {}
        self.knowledge_base = self._load_static_knowledge()
        
    def _load_static_knowledge(self) -> List[Dict]:
        """Load static knowledge base"""
        return [
            {
                "pattern": r"cancel|cancellation",
                "response": "RideSwift Cancellation Policy: Free cancellation up to 6 hours before pickup. 50% charge for 2-6 hours. Full charge for less than 2 hours.",
                "category": "policy"
            },
            {
                "pattern": r"price|cost|fare|rate",
                "response": "Our transparent pricing: Sedan ₹12/km, SUV ₹16/km, Luxury ₹25/km, Tempo ₹22/km. All prices include toll and GST.",
                "category": "pricing"
            },
            {
                "pattern": r"book|booking|ride",
                "response": "I'd be happy to help you book a ride! Please tell me:\n1. Pickup location\n2. Drop location\n3. Travel date and time\n4. Number of passengers",
                "category": "booking"
            },
            {
                "pattern": r"route|popular|cities",
                "response": "Popular routes: Hyderabad-Bangalore (570km), Hyderabad-Chennai (520km), Delhi-Jaipur (280km), Mumbai-Pune (150km)",
                "category": "routes"
            },
            {
                "pattern": r"safety|secure|covid",
                "response": "Your safety is our priority! All drivers are background verified, vehicles sanitized after each ride, GPS tracking available, and 24/7 support.",
                "category": "safety"
            }
        ]
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """Basic message analysis"""
        message_lower = message.lower()
        
        # Basic intent detection
        intent = "general_inquiry"
        if any(word in message_lower for word in ["book", "ride", "cab", "taxi"]):
            intent = "booking_request"
        elif any(word in message_lower for word in ["price", "cost", "fare", "rate"]):
            intent = "price_inquiry"
        elif any(word in message_lower for word in ["cancel", "refund"]):
            intent = "cancellation"
        elif any(word in message_lower for word in ["help", "support", "problem", "issue"]):
            intent = "support"
        elif any(word in message_lower for word in ["hello", "hi", "hey"]):
            intent = "greeting"
        
        # Basic sentiment
        sentiment = "neutral"
        if any(word in message_lower for word in ["angry", "frustrated", "terrible", "worst"]):
            sentiment = "negative"
        elif any(word in message_lower for word in ["happy", "great", "excellent", "love"]):
            sentiment = "positive"
        
        # Extract locations
        locations = []
        # Simple pattern for "from X to Y"
        route_pattern = r"from\s+(\w+)\s+to\s+(\w+)"
        route_match = re.search(route_pattern, message_lower)
        if route_match:
            locations = [route_match.group(1).title(), route_match.group(2).title()]
        
        return {
            "intent": intent,
            "intent_confidence": 0.8,
            "sentiment": sentiment.upper(),
            "sentiment_score": 0.8,
            "emotion": "neutral",
            "emotion_score": 0.8,
            "entities": {
                "locations": locations,
                "dates": [],
                "times": [],
                "persons": [],
                "money": []
            },
            "route": {"from": locations[0], "to": locations[1]} if len(locations) >= 2 else None,
            "has_urgency": any(word in message_lower for word in ["urgent", "asap", "emergency"]),
            "has_complaint": any(word in message_lower for word in ["complaint", "problem", "issue"])
        }
    
    async def get_user_context(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Get basic user context"""
        if not user_id:
            return {
                "user_name": "there",
                "booking_count": 0,
                "preferred_vehicle": None,
                "recent_routes": []
            }
        
        try:
            # Get user from database
            if self.db.database:
                user = await self.db.database.users.find_one({"_id": user_id})
            else:
                user = None
            if user:
                return {
                    "user_name": user.get("full_name", "there").split()[0],
                    "booking_count": 0,  # Would need to query bookings
                    "preferred_vehicle": "sedan",
                    "recent_routes": []
                }
        except:
            pass
        
        return {
            "user_name": "there",
            "booking_count": 0,
            "preferred_vehicle": None,
            "recent_routes": []
        }
    
    async def generate_response(
        self,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        llm_provider: AIProvider = AIProvider.OPENAI
    ) -> Dict[str, Any]:
        """Generate response using available AI or fallback"""
        
        # Analyze the message
        analysis = self.analyze_message(message)
        
        # Get user context
        user_context = await self.get_user_context(user_id)
        
        # Try to use AI if available
        if OPENAI_AVAILABLE and llm_provider == AIProvider.OPENAI:
            try:
                return await self._generate_openai_response(message, analysis, user_context, session_id)
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
        
        # Fallback to rule-based response
        return await self._generate_fallback_response(message, analysis, user_context, session_id)
    
    async def _generate_openai_response(
        self, 
        message: str, 
        analysis: Dict, 
        user_context: Dict,
        session_id: str
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        import openai
        
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Get conversation history
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        history = self.conversations[session_id][-10:]  # Last 10 messages
        
        # Build messages
        messages = [
            {
                "role": "system",
                "content": f"""You are Swift AI, an empathetic AI assistant for RideSwift cab booking.
                User: {user_context['user_name']}
                Be helpful, empathetic, and professional.
                Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                """
            }
        ]
        
        # Add history
        for msg in history:
            messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Generate response
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content
        
        # Store in history
        self.conversations[session_id].append({"role": "user", "content": message})
        self.conversations[session_id].append({"role": "assistant", "content": ai_response})
        
        # Generate suggestions
        suggestions = self._generate_suggestions(analysis)
        
        return {
            "response": ai_response,
            "metadata": {
                "intent": analysis["intent"],
                "confidence": analysis["intent_confidence"],
                "emotion": analysis["emotion"],
                "sentiment": analysis["sentiment"],
                "entities": analysis["entities"],
                "route": analysis["route"],
                "suggestions": suggestions,
                "session_id": session_id,
                "provider": "openai"
            }
        }
    
    async def _generate_fallback_response(
        self, 
        message: str, 
        analysis: Dict, 
        user_context: Dict,
        session_id: str
    ) -> Dict[str, Any]:
        """Generate rule-based fallback response"""
        
        # Check knowledge base
        response = None
        for knowledge in self.knowledge_base:
            if re.search(knowledge["pattern"], message.lower()):
                response = knowledge["response"]
                break
        
        # Default responses by intent
        if not response:
            intent_responses = {
                "greeting": f"Hello {user_context['user_name']}! 👋 Welcome to RideSwift. How can I help you today?",
                "booking_request": "I'd love to help you book a ride! Please provide:\n📍 Pickup location\n📍 Drop location\n📅 Travel date\n👥 Number of passengers",
                "price_inquiry": "Our transparent pricing:\n🚗 Sedan: ₹12/km\n🚙 SUV: ₹16/km\n💎 Luxury: ₹25/km\n🚐 Tempo: ₹22/km\n\nAll inclusive of toll and GST!",
                "support": "I'm here to help! For immediate assistance, call +91 8143243584. How can I assist you?",
                "cancellation": "Cancellation Policy:\n✅ Free: 6+ hours before\n⚠️ 50%: 2-6 hours before\n❌ Full charge: <2 hours\n\nNeed to cancel a booking?",
                "general_inquiry": "I'm here to help with bookings, pricing, or any questions about RideSwift. What would you like to know?"
            }
            response = intent_responses.get(analysis["intent"], intent_responses["general_inquiry"])
        
        # Add empathy for negative sentiment
        if analysis["sentiment"] == "NEGATIVE":
            response = f"I understand you might be frustrated, {user_context['user_name']}. " + response
        
        # Generate suggestions
        suggestions = self._generate_suggestions(analysis)
        
        return {
            "response": response,
            "metadata": {
                "intent": analysis["intent"],
                "confidence": analysis["intent_confidence"],
                "emotion": analysis["emotion"],
                "sentiment": analysis["sentiment"],
                "entities": analysis["entities"],
                "route": analysis["route"],
                "suggestions": suggestions,
                "session_id": session_id,
                "provider": "fallback"
            }
        }
    
    def _generate_suggestions(self, analysis: Dict) -> List[str]:
        """Generate contextual suggestions"""
        intent = analysis["intent"]
        
        suggestions_map = {
            "booking_request": ["Check prices", "Popular routes", "Available vehicles", "Help"],
            "price_inquiry": ["Calculate fare", "Book now", "Compare vehicles", "Discounts"],
            "support": ["Call support", "Email us", "FAQs", "Track booking"],
            "greeting": ["Book a ride", "Check prices", "My bookings", "Help"],
            "cancellation": ["View policy", "Cancel booking", "Contact support", "FAQs"],
            "general_inquiry": ["Book ride", "Pricing", "Support", "About us"]
        }
        
        return suggestions_map.get(intent, suggestions_map["general_inquiry"])
    
    async def train_on_feedback(self, message_id: str, feedback: str, user_id: str):
        """Store feedback for future improvements"""
        # In a real implementation, store this in database
        logger.info(f"Feedback received: {feedback} for message {message_id} from user {user_id}")

# Create singleton instance
ai_chatbot_service = LightweightAIChatbotService()
