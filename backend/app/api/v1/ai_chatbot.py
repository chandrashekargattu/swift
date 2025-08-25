"""
Advanced AI Chatbot API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
import asyncio
import logging
from datetime import datetime

from app.api.deps import get_current_user
from app.models.user import UserModel
from app.services.ai_chatbot import ai_chatbot_service, AIProvider

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    llm_provider: Optional[str] = "openai"

class ChatContext(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[ChatContext] = None
    llm_provider: Optional[AIProvider] = AIProvider.OPENAI
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class AnalysisRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

class AnalysisResponse(BaseModel):
    entities: Dict[str, List[str]]
    intent: str
    intent_confidence: float
    sentiment: str
    emotion: str
    route: Optional[Dict[str, str]]
    has_urgency: bool
    has_complaint: bool

class FeedbackRequest(BaseModel):
    message_id: str
    feedback: str = Field(..., pattern="^(positive|negative|helpful|not_helpful)$")
    user_id: Optional[str] = None
    comment: Optional[str] = None

class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

@router.post("/chat/public", response_model=ChatResponse)
async def public_chat(request: ChatMessage):
    """
    Public AI chat endpoint for unauthenticated users
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"anon_{datetime.now().timestamp()}"
        
        # Process message with basic service
        result = await ai_chatbot_service.generate_response(
            message=request.message,
            user_id="anonymous",
            session_id=session_id
        )
        
        return ChatResponse(
            response=result.get("response", "I'm sorry, I couldn't process that message."),
            session_id=session_id,
            metadata=result.get("metadata", {})
        )
    except Exception as e:
        logger.error(f"Public chat error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: Optional[UserModel] = Depends(get_current_user)
):
    """
    Advanced AI chat endpoint with RAG and multiple LLM support
    """
    try:
        # Use authenticated user if available, otherwise use context
        user_id = None
        if current_user:
            user_id = current_user.id
        elif request.context and request.context.user_id:
            user_id = request.context.user_id
        
        # Get session ID
        session_id = None
        if request.context and request.context.session_id:
            session_id = request.context.session_id
        
        # Generate response
        response = await ai_chatbot_service.generate_response(
            message=request.message,
            user_id=user_id,
            session_id=session_id,
            llm_provider=request.llm_provider
        )
        
        return ChatResponse(
            response=response["response"],
            metadata=response.get("metadata"),
            session_id=response.get("metadata", {}).get("session_id")
        )
        
    except Exception as e:
        # Log error
        print(f"Advanced chatbot error: {str(e)}")
        
        # Return friendly error response
        return ChatResponse(
            response="I apologize for the technical difficulty. Our team has been notified. For immediate assistance, please call +91 8143243584.",
            metadata={
                "error": True,
                "intent": "error",
                "suggestions": ["Try again", "Contact support", "Call +91 8143243584"]
            }
        )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_message(
    request: AnalysisRequest,
    current_user: Optional[UserModel] = Depends(get_current_user)
):
    """
    Analyze a message for entities, intent, sentiment, and emotion
    """
    analysis = ai_chatbot_service.analyze_message(request.message)
    
    return AnalysisResponse(**analysis)

@router.post("/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: Optional[UserModel] = Depends(get_current_user)
):
    """
    Submit feedback for continuous learning
    """
    user_id = current_user.id if current_user else request.user_id
    
    await ai_chatbot_service.train_on_feedback(
        message_id=request.message_id,
        feedback=f"{request.feedback}:{request.comment or ''}",
        user_id=user_id
    )
    
    return None

@router.post("/search-knowledge")
async def search_knowledge(request: KnowledgeSearchRequest):
    """
    Search the knowledge base
    """
    results = await ai_chatbot_service._search_knowledge_tool(request.query)
    
    return {
        "results": results,
        "query": request.query
    }

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat with streaming responses
    """
    await websocket.accept()
    session_id = None
    user_id = None
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Extract data
            message = data.get("message", "")
            session_id = data.get("session_id", session_id)
            user_id = data.get("user_id", user_id)
            llm_provider = AIProvider(data.get("llm_provider", "openai"))
            
            # Send typing indicator
            await websocket.send_json({
                "type": "typing",
                "data": {"typing": True}
            })
            
            # Generate response
            response = await ai_chatbot_service.generate_response(
                message=message,
                user_id=user_id,
                session_id=session_id,
                llm_provider=llm_provider
            )
            
            # Send response
            await websocket.send_json({
                "type": "message",
                "data": {
                    "response": response["response"],
                    "metadata": response.get("metadata"),
                    "session_id": session_id
                }
            })
            
            # Send typing indicator off
            await websocket.send_json({
                "type": "typing",
                "data": {"typing": False}
            })
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()

@router.get("/providers")
async def get_available_providers():
    """
    Get list of available AI providers
    """
    providers = []
    
    # Check if we're using the full AI service with LLM providers
    if hasattr(ai_chatbot_service, 'llm_providers'):
        if ai_chatbot_service.llm_providers.get(AIProvider.OPENAI):
            providers.append({
                "id": "openai",
                "name": "OpenAI GPT-4",
                "description": "Most advanced, best for complex queries"
            })
        
        if ai_chatbot_service.llm_providers.get(AIProvider.ANTHROPIC):
            providers.append({
                "id": "anthropic",
                "name": "Claude 3",
                "description": "Excellent for detailed, thoughtful responses"
            })
        
        if ai_chatbot_service.llm_providers.get(AIProvider.GOOGLE):
            providers.append({
                "id": "google",
                "name": "Google Gemini",
                "description": "Fast and efficient for general queries"
            })
    
    # Always include basic provider as fallback
    providers.append({
        "id": "basic",
        "name": "Basic Assistant",
        "description": "Simple rule-based responses (no AI)"
    })
    
    return {
        "providers": providers,
        "default": "openai" if len(providers) > 1 else "basic"
    }

@router.get("/health")
async def health_check():
    """
    Check AI service health
    """
    nlp_status = {}
    vector_status = {}
    
    # Check attributes only if they exist
    if hasattr(ai_chatbot_service, 'nlp'):
        nlp_status["spacy"] = bool(ai_chatbot_service.nlp)
    if hasattr(ai_chatbot_service, 'sentiment_analyzer'):
        nlp_status["sentiment"] = bool(ai_chatbot_service.sentiment_analyzer)
    if hasattr(ai_chatbot_service, 'intent_classifier'):
        nlp_status["intent"] = bool(ai_chatbot_service.intent_classifier)
    if hasattr(ai_chatbot_service, 'embeddings'):
        nlp_status["embeddings"] = bool(ai_chatbot_service.embeddings)
    
    if hasattr(ai_chatbot_service, 'chroma_client'):
        vector_status["chroma"] = bool(ai_chatbot_service.chroma_client)
    if hasattr(ai_chatbot_service, 'knowledge_collection'):
        vector_status["knowledge_loaded"] = bool(ai_chatbot_service.knowledge_collection)
    
    response = {
        "status": "healthy",
        "nlp_models": nlp_status,
        "vector_stores": vector_status
    }
    
    if hasattr(ai_chatbot_service, 'llm_providers'):
        response["llm_providers"] = list(ai_chatbot_service.llm_providers.keys())
    
    if hasattr(ai_chatbot_service, 'conversations'):
        response["active_sessions"] = len(ai_chatbot_service.conversations)
    
    return response
