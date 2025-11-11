"""
Inference script for Intent Classification System
"""

import os
import sys
import logging
import argparse
import numpy as np
from typing import List, Dict
import joblib

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.data.data_loader import load_config, DataLoader
from ml.traditional_ml.model import create_classifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntentPredictor:
    """Handle intent prediction for queries"""
    
    def __init__(self, config_path: str = 'config.yaml',
                 model_path: str = None,
                 intent_mapping_path: str = None):
        """
        Initialize predictor
        
        Args:
            config_path: Path to configuration file
            model_path: Path to trained model
            intent_mapping_path: Path to intent mapping
        """
        self.config = load_config(config_path)
        self.data_loader = DataLoader(self.config)
        
        # Load model
        self.classifier = create_classifier(self.config)
        
        if model_path:
            self.classifier.load_model(model_path)
        else:
            # Find latest model
            model_dir = self.config['training']['model_save_path']
            model_files = [f for f in os.listdir(model_dir) 
                          if f.endswith('.pkl') and 'model' in f and 'label' not in f and 'intent' not in f]
            if not model_files:
                raise FileNotFoundError("No model files found. Please train a model first.")
            latest_model = max(model_files, 
                             key=lambda x: os.path.getctime(os.path.join(model_dir, x)))
            model_path = os.path.join(model_dir, latest_model)
            self.classifier.load_model(model_path)
        
        logger.info(f"Model loaded from {model_path}")
        
        # Load intent mapping
        if intent_mapping_path:
            self.intent_mapping = joblib.load(intent_mapping_path)
        else:
            # Find latest intent mapping
            model_dir = self.config['training']['model_save_path']
            mapping_files = [f for f in os.listdir(model_dir) 
                           if f.startswith('intent_mapping') and f.endswith('.pkl')]
            if mapping_files:
                latest_mapping = max(mapping_files,
                                   key=lambda x: os.path.getctime(os.path.join(model_dir, x)))
                intent_mapping_path = os.path.join(model_dir, latest_mapping)
                self.intent_mapping = joblib.load(intent_mapping_path)
            else:
                raise FileNotFoundError("Intent mapping not found")
        
        logger.info(f"Intent mapping loaded: {len(self.intent_mapping)} intents")
        
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess query text
        
        Args:
            query: Input query
            
        Returns:
            Preprocessed query
        """
        return self.data_loader.preprocess_text(query)
    
    def predict(self, query: str) -> Dict:
        """
        Predict intent for a single query
        
        Args:
            query: Input query
            
        Returns:
            Dictionary with prediction results
        """
        # Preprocess
        processed_query = self.preprocess_query(query)
        
        # Predict
        y_pred = self.classifier.predict([processed_query])[0]
        y_proba = self.classifier.predict_proba([processed_query])[0]
        
        # Get top-k predictions
        top_k = self.config['inference']['return_top_k']
        top_indices = np.argsort(y_proba)[-top_k:][::-1]
        
        results = {
            'query': query,
            'predicted_intent': self.intent_mapping[y_pred],
            'confidence': float(y_proba[y_pred]),
            'top_predictions': [
                {
                    'intent': self.intent_mapping[idx],
                    'confidence': float(y_proba[idx])
                }
                for idx in top_indices
            ],
            'is_uncertain': y_proba[y_pred] < self.config['self_learning']['uncertainty_threshold']
        }
        
        return results
    
    def predict_batch(self, queries: List[str]) -> List[Dict]:
        """
        Predict intents for multiple queries
        
        Args:
            queries: List of input queries
            
        Returns:
            List of prediction results
        """
        results = []
        for query in queries:
            results.append(self.predict(query))
        return results
    
    def interactive_mode(self):
        """Run in interactive mode for testing"""
        print("\n" + "="*60)
        print("INTENT CLASSIFICATION - INTERACTIVE MODE")
        print("="*60)
        print("Enter queries to classify (or 'quit' to exit)")
        print("")
        
        while True:
            query = input("\nQuery: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            result = self.predict(query)
            
            print("\n" + "-"*60)
            print(f"Predicted Intent: {result['predicted_intent']}")
            print(f"Confidence: {result['confidence']:.4f}")
            
            if result['is_uncertain']:
                print("⚠️  Low confidence prediction - may need review")
            
            print("\nTop Predictions:")
            for i, pred in enumerate(result['top_predictions'], 1):
                print(f"  {i}. {pred['intent']}: {pred['confidence']:.4f}")
            print("-"*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intent Classification Inference")
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to model file')
    parser.add_argument('--intent-mapping', type=str, default=None,
                       help='Path to intent mapping file')
    parser.add_argument('--query', type=str, default=None,
                       help='Single query to classify')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    predictor = IntentPredictor(args.config, args.model, args.intent_mapping)
    
    if args.interactive or not args.query:
        predictor.interactive_mode()
    else:
        result = predictor.predict(args.query)
        print(f"\nQuery: {result['query']}")
        print(f"Predicted Intent: {result['predicted_intent']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print("\nTop Predictions:")
        for i, pred in enumerate(result['top_predictions'], 1):
            print(f"  {i}. {pred['intent']}: {pred['confidence']:.4f}")

