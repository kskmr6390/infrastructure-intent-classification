"""
Predictor Manager for handling ML model predictions
"""

import logging
from typing import Dict, Any
from backend.core.config import Settings, load_ml_config
from backend.core.observability import get_observability_manager
from backend.core.local_observability import get_local_observability_store

logger = logging.getLogger(__name__)


class PredictorManager:
    """
    Manages ML model loading and predictions
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize predictor manager
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.config = load_ml_config(settings.ML_CONFIG_PATH)
        self.predictor = None
        self.predictor_type = None
        
        # Initialize observability (both local and cloud)
        obs_config = self.config.get('observability', {})
        self.observability = get_observability_manager(obs_config)
        self.local_obs = get_local_observability_store(obs_config)
        
    async def initialize(self):
        """Initialize the predictor"""
        try:
            # Try to import LLM predictor first
            try:
                from ml.llm.inference_llm import LLMIntentPredictor
                self.predictor = LLMIntentPredictor()
                self.predictor_type = 'llm'
                logger.info(f"LLM Predictor initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to load LLM predictor: {e}")
                # Fall back to traditional predictor
                from ml.traditional_ml.inference import IntentPredictor
                self.predictor = IntentPredictor()
                self.predictor_type = 'traditional'
                logger.info("Traditional predictor initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize any predictor: {e}")
            self.predictor = None
            
    def is_ready(self) -> bool:
        """Check if predictor is ready"""
        return self.predictor is not None
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Make prediction
        
        Args:
            text: Input text to classify
            
        Returns:
            Prediction result dictionary
        """
        if not self.is_ready():
            raise RuntimeError("Predictor not initialized")
        
        result = self.predictor.predict(text)
        
        # Convert numpy types to Python native types for JSON serialization
        prediction = {
            'predicted_intent': str(result['predicted_intent']),
            'confidence': float(result['confidence']),
            'top_predictions': [
                {
                    'intent': str(pred['intent']),
                    'confidence': float(pred['confidence'])
                }
                for pred in result['top_predictions']
            ],
            'is_uncertain': bool(result['is_uncertain'])
        }
        
        # Prepare metadata for logging
        log_metadata = {
            'predictor_type': self.predictor_type,
            'model_type': self.config.get('model', {}).get('type', 'unknown'),
            'is_uncertain': prediction['is_uncertain'],
            'is_out_of_scope': prediction.get('is_out_of_scope', False)
        }
        
        # Log prediction to Local Observability (always enabled)
        try:
            self.local_obs.log_prediction(
                query=text,
                predicted_intent=prediction['predicted_intent'],
                confidence=prediction['confidence'],
                all_predictions=prediction['top_predictions'],
                metadata=log_metadata
            )
        except Exception as e:
            logger.warning(f"Failed to log prediction locally: {e}")
        
        # Log prediction to LangSmith (if enabled)
        try:
            self.observability.log_prediction(
                query=text,
                predicted_intent=prediction['predicted_intent'],
                confidence=prediction['confidence'],
                all_predictions=prediction['top_predictions'],
                metadata=log_metadata
            )
        except Exception as e:
            logger.warning(f"Failed to log prediction to LangSmith: {e}")
        
        return prediction
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            'predictor_type': self.predictor_type,
            'is_ready': self.is_ready(),
            'model_config': self.config.get('model', {})
        }

