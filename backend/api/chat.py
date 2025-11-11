"""
Chat API endpoints
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import logging

from backend.database.db import ChatDatabase
from backend.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    session_id: str
    message: str


class PredictionInfo(BaseModel):
    """Prediction information"""
    intent: str
    confidence: float


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    user_message_id: int = None
    assistant_message_id: int = None
    response: str = None
    prediction: Dict[str, Any] = None
    error: str = None


@router.post("/chat", response_model=ChatResponse)
async def process_chat(request: Request, chat_request: ChatRequest):
    """
    Process chat message and return intent prediction
    
    Args:
        chat_request: Chat request with session_id and message
        
    Returns:
        Chat response with prediction
    """
    try:
        predictor_manager = request.app.state.predictor_manager
        
        if not predictor_manager.is_ready():
            raise HTTPException(
                status_code=500,
                detail="Model not initialized. Please train a model first."
            )
        
        # Initialize database
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        # Verify session exists
        session_data = db.get_session(chat_request.session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Save user message
        user_message_id = db.add_message(
            session_id=chat_request.session_id,
            role='user',
            content=chat_request.message
        )
        
        # Get prediction
        result = predictor_manager.predict(chat_request.message)
        
        # Check if query is out of scope
        if result.get('is_out_of_scope', False):
            assistant_message = f"🚫 **Out of Scope Query**\n\n"
            assistant_message += result.get('rejection_message', 
                "This query doesn't appear to be related to infrastructure.")
            assistant_message += f"\n\n**Confidence:** {result['confidence']:.2%}"
            assistant_message += "\n\n💡 **Try asking about:**\n"
            assistant_message += "- Network interface status\n"
            assistant_message += "- System resource usage (CPU, memory)\n"
            assistant_message += "- Security alerts and vulnerabilities\n"
            assistant_message += "- Device configurations\n"
            assistant_message += "- Performance metrics and bandwidth\n"
        else:
            # Format normal assistant response
            assistant_message = f"**Intent Detected:** {result['predicted_intent']}\n"
            assistant_message += f"**Confidence:** {result['confidence']:.2%}\n\n"
            
            if result['is_uncertain']:
                assistant_message += "⚠️ **Low Confidence Warning:** This prediction has low confidence. "
                assistant_message += "Please verify the result.\n\n"
            
            if result['top_predictions']:
                assistant_message += "**Top Predictions:**\n"
                for i, pred in enumerate(result['top_predictions'][:3], 1):
                    assistant_message += f"{i}. {pred['intent']}: {pred['confidence']:.2%}\n"
        
        # Save assistant message
        assistant_message_id = db.add_message(
            session_id=chat_request.session_id,
            role='assistant',
            content=assistant_message,
            predicted_intent=result['predicted_intent'],
            confidence=result['confidence'],
            top_predictions=result['top_predictions'],
            is_uncertain=result['is_uncertain']
        )
        
        # Save uncertain prediction for review if needed
        if result['is_uncertain']:
            from ml.data.self_learning import SelfLearningSystem
            self_learning = SelfLearningSystem()
            uncertain_samples = [{
                'query': chat_request.message,
                'predicted_label': result['predicted_intent'],
                'max_probability': result['confidence'],
                'timestamp': datetime.now().isoformat(),
                'needs_review': True,
                'session_id': chat_request.session_id,
                'message_id': int(assistant_message_id)
            }]
            self_learning.save_uncertain_predictions(uncertain_samples)
        
        return ChatResponse(
            success=True,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id,
            response=assistant_message,
            prediction=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

