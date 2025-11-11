"""
Health check API endpoints
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    success: bool
    status: str
    model_loaded: bool
    model_info: Dict[str, Any] = None
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint"""
    predictor_manager = request.app.state.predictor_manager
    
    return HealthResponse(
        success=True,
        status='healthy',
        model_loaded=predictor_manager.is_ready(),
        model_info=predictor_manager.get_model_info(),
        timestamp=datetime.now().isoformat()
    )

