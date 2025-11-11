"""
FastAPI Backend for Intent Classification System
Main application entry point
"""

import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.core.config import get_settings
from backend.api import chat, sessions, feedback, health, observability
from backend.core.predictor import PredictorManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global predictor manager
predictor_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    global predictor_manager
    settings = get_settings()
    
    logger.info("Initializing Intent Classification System...")
    predictor_manager = PredictorManager(settings)
    await predictor_manager.initialize()
    
    app.state.predictor_manager = predictor_manager
    logger.info("System initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Intent Classification System...")


# Create FastAPI app
app = FastAPI(
    title="Intent Classification API",
    description="Machine Learning based Intent Classification System for Infrastructure Copilot",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(observability.router, prefix="/api", tags=["observability"])

# Mount static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

# Mount guides directory for web access
guides_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "guides")
app.mount("/guides", StaticFiles(directory=guides_path, html=True), name="guides")


@app.get("/")
async def root():
    """Serve the main chat interface"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    return FileResponse(os.path.join(frontend_path, "templates", "chat.html"))


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    print("\n" + "="*60)
    print("Intent Classification System - FastAPI Backend")
    print("="*60)
    print(f"Starting server at http://{settings.HOST}:{settings.PORT}")
    print(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

