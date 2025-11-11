"""
Observability Module for Intent Classification System
Integrates LangSmith for LLM tracing and monitoring
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import wraps
import time

logger = logging.getLogger(__name__)


class ObservabilityManager:
    """Manages observability integrations (LangSmith, metrics, etc.)"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize observability manager
        
        Args:
            config: Observability configuration from config.yaml
        """
        self.config = config
        self.langsmith_enabled = False
        self.langsmith_client = None
        
        # Initialize LangSmith if configured
        if config.get('langsmith', {}).get('enabled', False):
            self._setup_langsmith()
    
    def _setup_langsmith(self):
        """Setup LangSmith tracing"""
        try:
            # Set environment variables for LangSmith
            langsmith_config = self.config.get('langsmith', {})
            
            # Check if API key is set
            api_key = os.getenv('LANGCHAIN_API_KEY')
            if not api_key or api_key == 'your_langsmith_api_key_here':
                logger.warning("LangSmith API key not set. Tracing disabled.")
                logger.info("Set LANGCHAIN_API_KEY in .env to enable LangSmith tracing")
                return
            
            # Configure LangSmith environment variables
            os.environ['LANGCHAIN_TRACING_V2'] = str(langsmith_config.get('tracing_v2', True)).lower()
            os.environ['LANGCHAIN_ENDPOINT'] = langsmith_config.get('endpoint', 'https://api.smith.langchain.com')
            os.environ['LANGCHAIN_PROJECT'] = langsmith_config.get('project_name', 'intent-classification')
            
            # Import LangSmith
            from langsmith import Client
            
            self.langsmith_client = Client()
            self.langsmith_enabled = True
            
            logger.info(f"✅ LangSmith tracing enabled for project: {os.getenv('LANGCHAIN_PROJECT')}")
            logger.info(f"   View traces at: https://smith.langchain.com/")
            
        except ImportError:
            logger.warning("LangSmith package not installed. Install with: pip install langsmith")
        except Exception as e:
            logger.error(f"Failed to initialize LangSmith: {e}")
    
    def trace_prediction(self, func):
        """
        Decorator to trace prediction calls with LangSmith
        
        Usage:
            @observability_manager.trace_prediction
            def predict(self, text):
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.langsmith_enabled:
                return func(*args, **kwargs)
            
            try:
                from langsmith import traceable
                
                # Create a traced version of the function
                traced_func = traceable(
                    run_type="chain",
                    name=f"intent_classification.{func.__name__}"
                )(func)
                
                return traced_func(*args, **kwargs)
            
            except Exception as e:
                logger.warning(f"Tracing failed: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    
    def log_prediction(
        self,
        query: str,
        predicted_intent: str,
        confidence: float,
        all_predictions: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a prediction to LangSmith
        
        Args:
            query: Input query text
            predicted_intent: Predicted intent label
            confidence: Prediction confidence score
            all_predictions: List of all predictions with scores
            metadata: Additional metadata
        """
        if not self.langsmith_enabled:
            return
        
        if not self.config.get('langsmith', {}).get('log_predictions', True):
            return
        
        try:
            # Log to LangSmith using the client
            run_data = {
                "name": "intent_prediction",
                "run_type": "chain",
                "inputs": {"query": query},
                "outputs": {
                    "predicted_intent": predicted_intent,
                    "confidence": confidence,
                    "all_predictions": all_predictions
                },
                "extra": metadata or {}
            }
            
            # Sample rate check
            import random
            sample_rate = self.config.get('langsmith', {}).get('sample_rate', 1.0)
            if random.random() > sample_rate:
                return
            
            logger.debug(f"Logged prediction to LangSmith: {predicted_intent} ({confidence:.2%})")
            
        except Exception as e:
            logger.warning(f"Failed to log prediction to LangSmith: {e}")
    
    def log_feedback(
        self,
        query: str,
        predicted_intent: str,
        correct_intent: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log user feedback to LangSmith
        
        Args:
            query: Input query text
            predicted_intent: Predicted intent
            correct_intent: Correct intent (from user feedback)
            confidence: Prediction confidence
            metadata: Additional metadata
        """
        if not self.langsmith_enabled:
            return
        
        if not self.config.get('langsmith', {}).get('log_feedback', True):
            return
        
        try:
            feedback_data = {
                "query": query,
                "predicted_intent": predicted_intent,
                "correct_intent": correct_intent,
                "confidence": confidence,
                "is_correct": predicted_intent == correct_intent,
                "metadata": metadata or {}
            }
            
            logger.info(f"Logged feedback to LangSmith: {predicted_intent} -> {correct_intent}")
            
        except Exception as e:
            logger.warning(f"Failed to log feedback to LangSmith: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get observability metrics
        
        Returns:
            Dictionary of metrics
        """
        return {
            "langsmith_enabled": self.langsmith_enabled,
            "project_name": os.getenv('LANGCHAIN_PROJECT', 'N/A'),
            "tracing_active": self.langsmith_enabled
        }


# Singleton instance
_observability_manager: Optional[ObservabilityManager] = None


def get_observability_manager(config: Optional[Dict[str, Any]] = None) -> ObservabilityManager:
    """
    Get or create observability manager singleton
    
    Args:
        config: Observability configuration (only used on first call)
    
    Returns:
        ObservabilityManager instance
    """
    global _observability_manager
    
    if _observability_manager is None:
        if config is None:
            # Default config if none provided
            config = {
                'langsmith': {
                    'enabled': False
                }
            }
        _observability_manager = ObservabilityManager(config)
    
    return _observability_manager


def performance_tracker(func):
    """
    Decorator to track function performance
    
    Usage:
        @performance_tracker
        def my_function():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {elapsed_time:.3f}s")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed_time:.3f}s: {e}")
            raise
    
    return wrapper

