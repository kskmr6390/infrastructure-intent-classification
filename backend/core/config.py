"""
Configuration management for FastAPI backend
"""

import os
import yaml
from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Intent Classification System"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_PATH: str = "backend/database/chat_sessions.db"
    
    # ML Configuration
    ML_CONFIG_PATH: str = "config.yaml"
    
    # Paths
    MODELS_PATH: str = "ml/model/saved_models"
    FEEDBACK_PATH: str = "ml/data/feedback"
    LOGS_PATH: str = "logs"
    
    # LangSmith / Observability (optional - will be None if not set)
    LANGCHAIN_TRACING_V2: Optional[str] = None
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def load_ml_config(config_path: str = None) -> dict:
    """
    Load ML configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        settings = get_settings()
        config_path = settings.ML_CONFIG_PATH
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

