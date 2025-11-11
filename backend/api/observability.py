"""
Observability API endpoints for local monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from backend.core.local_observability import get_local_observability_store

logger = logging.getLogger(__name__)

router = APIRouter()


class ObservabilityStatsResponse(BaseModel):
    """Observability statistics response"""
    success: bool
    statistics: Dict[str, Any] = None
    error: str = None


class ObservabilityExportResponse(BaseModel):
    """Export response"""
    success: bool
    exported_files: Dict[str, str] = None
    message: str = None
    error: str = None


class RecentPredictionsResponse(BaseModel):
    """Recent predictions response"""
    success: bool
    predictions: List[Dict[str, Any]] = None
    count: int = 0
    error: str = None


class IntentPerformanceResponse(BaseModel):
    """Intent performance response"""
    success: bool
    intent_performance: Dict[str, Any] = None
    error: str = None


@router.get("/observability/stats", response_model=ObservabilityStatsResponse)
async def get_observability_stats(
    time_range: Optional[str] = Query(None, description="Time range: '24h', '7d', or '30d'")
):
    """
    Get observability statistics
    
    Query Parameters:
        - time_range: Optional time range filter
    
    Returns:
        Comprehensive statistics including:
        - Total predictions
        - Average confidence
        - Out-of-scope rate
        - Feedback accuracy
        - Top predicted intents
        - Confidence distribution
    """
    try:
        local_obs = get_local_observability_store()
        stats = local_obs.get_statistics(time_range=time_range)
        
        return ObservabilityStatsResponse(
            success=True,
            statistics=stats
        )
        
    except Exception as e:
        logger.error(f"Error getting observability stats: {e}")
        return ObservabilityStatsResponse(
            success=False,
            error=str(e)
        )


@router.get("/observability/recent", response_model=RecentPredictionsResponse)
async def get_recent_predictions(
    limit: int = Query(100, description="Number of recent predictions to return")
):
    """
    Get recent predictions
    
    Query Parameters:
        - limit: Number of predictions to return (default: 100)
    
    Returns:
        List of recent predictions with all details
    """
    try:
        local_obs = get_local_observability_store()
        predictions = local_obs.get_recent_predictions(limit=limit)
        
        return RecentPredictionsResponse(
            success=True,
            predictions=predictions,
            count=len(predictions)
        )
        
    except Exception as e:
        logger.error(f"Error getting recent predictions: {e}")
        return RecentPredictionsResponse(
            success=False,
            error=str(e)
        )


@router.get("/observability/intent-performance", response_model=IntentPerformanceResponse)
async def get_intent_performance():
    """
    Get per-intent performance statistics
    
    Returns:
        Performance metrics for each intent including:
        - Prediction counts
        - Average confidence
        - Uncertainty rates
        - Feedback accuracy
    """
    try:
        local_obs = get_local_observability_store()
        performance = local_obs.get_intent_performance()
        
        return IntentPerformanceResponse(
            success=True,
            intent_performance=performance
        )
        
    except Exception as e:
        logger.error(f"Error getting intent performance: {e}")
        return IntentPerformanceResponse(
            success=False,
            error=str(e)
        )


@router.post("/observability/export", response_model=ObservabilityExportResponse)
async def export_observability_data():
    """
    Export all observability data to JSON files
    
    Returns:
        Paths to exported files
    """
    try:
        local_obs = get_local_observability_store()
        exported_files = local_obs.export_data()
        
        return ObservabilityExportResponse(
            success=True,
            exported_files=exported_files,
            message=f"Exported {len(exported_files)} files successfully"
        )
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return ObservabilityExportResponse(
            success=False,
            error=str(e)
        )


@router.delete("/observability/cleanup")
async def cleanup_old_data(days: int = Query(30, description="Keep data newer than X days")):
    """
    Clean up old observability data
    
    Query Parameters:
        - days: Keep data newer than this many days (default: 30)
    
    Returns:
        Success message
    """
    try:
        local_obs = get_local_observability_store()
        local_obs.clear_old_data(days=days)
        
        return {
            "success": True,
            "message": f"Cleaned up data older than {days} days"
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

