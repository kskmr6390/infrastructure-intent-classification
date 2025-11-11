"""
LLM-based Inference for Intent Classification
"""

import os
import sys
import logging
import numpy as np
from typing import List, Dict
import joblib

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.data.data_loader import load_config, DataLoader
from ml.llm.llm_model import LLMIntentClassifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LLMIntentPredictor:
    """Handle LLM-based intent prediction"""
    
    def __init__(self, config_path: str = 'config.yaml',
                 model_path: str = None,
                 intent_mapping_path: str = None):
        """
        Initialize LLM predictor
        
        Args:
            config_path: Path to configuration file
            model_path: Path to trained LLM model
            intent_mapping_path: Path to intent mapping
        """
        self.config = load_config(config_path)
        self.data_loader = DataLoader(self.config)
        
        # Load LLM model
        self.classifier = LLMIntentClassifier(self.config)
        
        if model_path:
            self.classifier.load_saved_model(model_path)
        else:
            # Find latest LLM model
            model_dir = self.config['training']['model_save_path']
            model_files = [f for f in os.listdir(model_dir) 
                          if f.startswith('llm_model') and f.endswith('.pkl')]
            if not model_files:
                raise FileNotFoundError("No LLM model files found. Please train an LLM model first.")
            latest_model = max(model_files, 
                             key=lambda x: os.path.getctime(os.path.join(model_dir, x)))
            model_path = os.path.join(model_dir, latest_model)
            self.classifier.load_saved_model(model_path)
        
        logger.info(f"LLM model loaded from {model_path}")
        
        # Load intent mapping
        if intent_mapping_path:
            self.intent_mapping = joblib.load(intent_mapping_path)
        else:
            # Find latest intent mapping for LLM
            model_dir = self.config['training']['model_save_path']
            mapping_files = [f for f in os.listdir(model_dir) 
                           if f.startswith('llm_intent_mapping') and f.endswith('.pkl')]
            if mapping_files:
                latest_mapping = max(mapping_files,
                                   key=lambda x: os.path.getctime(os.path.join(model_dir, x)))
                intent_mapping_path = os.path.join(model_dir, latest_mapping)
                self.intent_mapping = joblib.load(intent_mapping_path)
            else:
                raise FileNotFoundError("LLM intent mapping not found")
        
        logger.info(f"Intent mapping loaded: {len(self.intent_mapping)} intents")
        
    def preprocess_query(self, query: str) -> str:
        """Preprocess query text"""
        return self.data_loader.preprocess_text(query)
    
    def predict(self, query: str) -> Dict:
        """
        Predict intent for a single query with out-of-scope detection
        
        Args:
            query: Input query
            
        Returns:
            Dictionary with prediction results or rejection message
        """
        # Preprocess
        processed_query = self.preprocess_query(query)
        
        # Predict
        y_pred = self.classifier.predict([processed_query])[0]
        y_proba = self.classifier.predict_proba([processed_query])[0]
        
        # Get confidence for predicted intent
        max_confidence = float(y_proba[y_pred])
        
        # Check if query is out of scope (infrastructure-only mode)
        out_of_scope_threshold = self.config['inference'].get('out_of_scope_threshold', 0.5)
        strict_mode = self.config['inference'].get('strict_infrastructure_only', True)
        
        if strict_mode and max_confidence < out_of_scope_threshold:
            # Query is likely not related to infrastructure
            rejection_msg = self.config['inference'].get('rejection_message',
                "This query doesn't appear to be related to infrastructure. Please ask about network, security, or system infrastructure topics.")
            
            return {
                'query': query,
                'predicted_intent': 'out_of_scope',
                'confidence': max_confidence,
                'is_out_of_scope': True,
                'rejection_message': rejection_msg,
                'top_predictions': [],
                'is_uncertain': True,
                'model_type': 'llm'
            }
        
        # Get top-k predictions
        top_k = self.config['inference']['return_top_k']
        top_indices = np.argsort(y_proba)[-top_k:][::-1]
        
        results = {
            'query': query,
            'predicted_intent': self.intent_mapping[y_pred],
            'confidence': max_confidence,
            'is_out_of_scope': False,
            'top_predictions': [
                {
                    'intent': self.intent_mapping[idx],
                    'confidence': float(y_proba[idx])
                }
                for idx in top_indices
            ],
            'is_uncertain': max_confidence < self.config['self_learning']['uncertainty_threshold'],
            'model_type': 'llm'
        }
        
        return results
    
    def predict_batch(self, queries: List[str]) -> List[Dict]:
        """Predict intents for multiple queries"""
        results = []
        for query in queries:
            results.append(self.predict(query))
        return results


if __name__ == "__main__":
    predictor = LLMIntentPredictor()
    
    print("\n" + "="*60)
    print("LLM INTENT CLASSIFICATION - INTERACTIVE MODE")
    print("="*60)
    print(f"Model: {predictor.config['model']['llm']['model_name']}")
    print(f"Intents: {len(predictor.intent_mapping)}")
    print("Enter queries to classify (or 'quit' to exit)")
    print("")
    
    while True:
        query = input("\nQuery: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        result = predictor.predict(query)
        
        print("\n" + "-"*60)
        print(f"🎯 Predicted Intent: {result['predicted_intent']}")
        print(f"📊 Confidence: {result['confidence']:.4f} ({result['confidence']*100:.1f}%)")
        
        if result['is_uncertain']:
            print("⚠️  Low confidence prediction - may need review")
        else:
            print("✅ High confidence prediction")
        
        print("\n📋 Top 3 Predictions:")
        for i, pred in enumerate(result['top_predictions'], 1):
            print(f"   {i}. {pred['intent']}: {pred['confidence']:.4f} ({pred['confidence']*100:.1f}%)")
        print("-"*60)

