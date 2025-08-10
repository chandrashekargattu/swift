"""
Advanced AI Chatbot API endpoints
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json
import asyncio

from app.api.deps import get_current_user
from app.models.user import UserModel
from app.services.ai_chatbot import ai_chatbot_service, AIProvider

router = APIRouter()

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
    
    return {
        "providers": providers,
        "default": "openai" if providers else None
    }

@router.get("/health")
async def health_check():
    """
    Check AI service health
    """
    return {
        "status": "healthy",
        "nlp_models": {
            "spacy": bool(ai_chatbot_service.nlp),
            "sentiment": bool(ai_chatbot_service.sentiment_analyzer),
            "intent": bool(ai_chatbot_service.intent_classifier),
            "embeddings": bool(ai_chatbot_service.embeddings)
        },
        "vector_stores": {
            "chroma": bool(ai_chatbot_service.chroma_client),
            "knowledge_loaded": bool(ai_chatbot_service.knowledge_collection)
        },
        "llm_providers": list(ai_chatbot_service.llm_providers.keys()),
        "active_sessions": len(ai_chatbot_service.conversations)
    }
