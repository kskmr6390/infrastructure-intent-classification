"""
Feedback API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

from backend.database.db import ChatDatabase
from backend.core.config import get_settings
from backend.core.observability import get_observability_manager
from backend.core.local_observability import get_local_observability_store

logger = logging.getLogger(__name__)

router = APIRouter()


class FeedbackRequest(BaseModel):
    """Feedback request model"""
    message_id: int
    session_id: str
    query: str
    predicted_intent: str
    correct_intent: str
    confidence: float


class FeedbackResponse(BaseModel):
    """Feedback response model"""
    success: bool
    feedback_id: int = None
    message: str = None
    statistics: Dict[str, Any] = None
    error: str = None


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a prediction"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        # Save feedback to database
        feedback_id = db.add_feedback(
            message_id=request.message_id,
            session_id=request.session_id,
            query=request.query,
            predicted_intent=request.predicted_intent,
            correct_intent=request.correct_intent,
            confidence=request.confidence
        )
        
        # Add to self-learning system
        from ml.data.self_learning import SelfLearningSystem
        self_learning = SelfLearningSystem()
        self_learning.add_feedback(
            query=request.query,
            predicted_intent=request.predicted_intent,
            correct_intent=request.correct_intent,
            confidence=request.confidence
        )
        
        # Prepare feedback metadata
        feedback_metadata = {
            'message_id': request.message_id,
            'session_id': request.session_id,
            'feedback_id': feedback_id
        }
        
        # Log feedback to Local Observability
        try:
            local_obs = get_local_observability_store()
            local_obs.log_feedback(
                query=request.query,
                predicted_intent=request.predicted_intent,
                correct_intent=request.correct_intent,
                confidence=request.confidence,
                metadata=feedback_metadata
            )
        except Exception as e:
            logger.warning(f"Failed to log feedback locally: {e}")
        
        # Log feedback to LangSmith (if enabled)
        try:
            observability = get_observability_manager()
            observability.log_feedback(
                query=request.query,
                predicted_intent=request.predicted_intent,
                correct_intent=request.correct_intent,
                confidence=request.confidence,
                metadata=feedback_metadata
            )
        except Exception as e:
            logger.warning(f"Failed to log feedback to LangSmith: {e}")
        
        return FeedbackResponse(
            success=True,
            feedback_id=feedback_id,
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=FeedbackResponse)
async def get_statistics():
    """Get overall statistics"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        # Get session count
        sessions = db.get_all_sessions()
        
        # Get feedback statistics
        from ml.data.self_learning import SelfLearningSystem
        self_learning = SelfLearningSystem()
        feedback_stats = self_learning.get_feedback_statistics()
        
        # Get all messages count
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM messages')
        message_count = cursor.fetchone()['count']
        conn.close()
        
        stats = {
            'total_sessions': len(sessions),
            'total_messages': message_count,
            'feedback_stats': feedback_stats
        }
        
        return FeedbackResponse(
            success=True,
            statistics=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export_feedback", response_model=FeedbackResponse)
async def export_feedback():
    """Export feedback for retraining"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        output_path = f'{settings.FEEDBACK_PATH}/exported_feedback.jsonl'
        db.export_feedback_to_jsonl(output_path)
        
        return FeedbackResponse(
            success=True,
            message=f'Feedback exported to {output_path}'
        )
        
    except Exception as e:
        logger.error(f"Error exporting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

