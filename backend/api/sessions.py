"""
Session management API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from backend.database.db import ChatDatabase
from backend.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateSessionRequest(BaseModel):
    """Create session request model"""
    session_name: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    """Update session request model"""
    session_name: str


class SessionResponse(BaseModel):
    """Session response model"""
    success: bool
    session: Dict[str, Any] = None
    sessions: List[Dict[str, Any]] = None
    messages: List[Dict[str, Any]] = None
    statistics: Dict[str, Any] = None
    message: str = None
    error: str = None


@router.get("/sessions", response_model=SessionResponse)
async def get_sessions():
    """Get all chat sessions"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        sessions = db.get_all_sessions()
        
        return SessionResponse(
            success=True,
            sessions=sessions
        )
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        session_id = db.create_session(request.session_name)
        session_data = db.get_session(session_id)
        
        return SessionResponse(
            success=True,
            session=session_data
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details and messages"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        session_data = db.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.get_session_messages(session_id)
        stats = db.get_session_statistics(session_id)
        
        return SessionResponse(
            success=True,
            session=session_data,
            messages=messages,
            statistics=stats
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update session name"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        db.update_session_name(session_id, request.session_name)
        
        return SessionResponse(
            success=True,
            message="Session updated successfully"
        )
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}", response_model=SessionResponse)
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        settings = get_settings()
        db = ChatDatabase(settings.DATABASE_PATH)
        
        db.delete_session(session_id)
        
        return SessionResponse(
            success=True,
            message="Session deleted successfully"
        )
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

