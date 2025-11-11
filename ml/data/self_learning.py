"""
Self-Learning Module for Intent Classification System
Implements active learning and continuous improvement
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
import joblib
from ml.data.data_loader import DataLoader, load_config
from ml.traditional_ml.model import create_classifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SelfLearningSystem:
    """Self-learning system with active learning capabilities"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize self-learning system
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.feedback_storage = self.config['self_learning']['feedback_storage_path']
        os.makedirs(self.feedback_storage, exist_ok=True)
        
        self.feedback_file = os.path.join(self.feedback_storage, 'feedback.jsonl')
        self.uncertain_predictions_file = os.path.join(
            self.feedback_storage, 'uncertain_predictions.jsonl'
        )
        
        # Initialize feedback counter
        self.feedback_count = self._count_feedback_samples()
        
    def _count_feedback_samples(self) -> int:
        """Count existing feedback samples"""
        if not os.path.exists(self.feedback_file):
            return 0
        
        count = 0
        with open(self.feedback_file, 'r') as f:
            for _ in f:
                count += 1
        return count
    
    def calculate_uncertainty(self, probabilities: np.ndarray) -> float:
        """
        Calculate prediction uncertainty using entropy
        
        Args:
            probabilities: Prediction probabilities
            
        Returns:
            Uncertainty score
        """
        # Entropy-based uncertainty
        entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))
        return float(entropy)
    
    def calculate_margin(self, probabilities: np.ndarray) -> float:
        """
        Calculate margin between top two predictions
        
        Args:
            probabilities: Prediction probabilities
            
        Returns:
            Margin score
        """
        sorted_probs = np.sort(probabilities)
        margin = sorted_probs[-1] - sorted_probs[-2]
        return float(margin)
    
    def identify_uncertain_predictions(self, queries: List[str], 
                                      predictions: np.ndarray,
                                      probabilities: np.ndarray) -> List[Dict]:
        """
        Identify predictions with high uncertainty
        
        Args:
            queries: List of queries
            predictions: Predicted labels
            probabilities: Prediction probabilities
            
        Returns:
            List of uncertain predictions
        """
        uncertain_samples = []
        threshold = self.config['self_learning']['uncertainty_threshold']
        
        for i, (query, pred, proba) in enumerate(zip(queries, predictions, probabilities)):
            max_prob = np.max(proba)
            uncertainty = self.calculate_uncertainty(proba)
            margin = self.calculate_margin(proba)
            
            if max_prob < threshold:
                uncertain_samples.append({
                    'query': query,
                    'predicted_label': int(pred),
                    'max_probability': float(max_prob),
                    'uncertainty': uncertainty,
                    'margin': margin,
                    'timestamp': datetime.now().isoformat(),
                    'needs_review': True
                })
        
        return uncertain_samples
    
    def save_uncertain_predictions(self, uncertain_samples: List[Dict]):
        """
        Save uncertain predictions for human review
        
        Args:
            uncertain_samples: List of uncertain predictions
        """
        if not uncertain_samples:
            return
        
        logger.info(f"Saving {len(uncertain_samples)} uncertain predictions for review")
        
        with open(self.uncertain_predictions_file, 'a') as f:
            for sample in uncertain_samples:
                f.write(json.dumps(sample) + '\n')
    
    def add_feedback(self, query: str, predicted_intent: str, 
                    correct_intent: str, confidence: float):
        """
        Add feedback for a prediction
        
        Args:
            query: Original query
            predicted_intent: Predicted intent
            correct_intent: Correct intent (from human feedback)
            confidence: Prediction confidence
        """
        feedback = {
            'query': query,
            'predicted_intent': predicted_intent,
            'correct_intent': correct_intent,
            'confidence': confidence,
            'is_correct': predicted_intent == correct_intent,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self.feedback_file, 'a') as f:
            f.write(json.dumps(feedback) + '\n')
        
        self.feedback_count += 1
        logger.info(f"Feedback added: {feedback}")
        
        # Check if we should retrain
        if (self.config['self_learning']['auto_retrain'] and 
            self.feedback_count >= self.config['self_learning']['min_samples_for_retrain']):
            logger.info("Sufficient feedback collected. Triggering retraining...")
            self.retrain_with_feedback()
    
    def load_feedback_data(self) -> pd.DataFrame:
        """
        Load all feedback data
        
        Returns:
            DataFrame with feedback data
        """
        if not os.path.exists(self.feedback_file):
            return pd.DataFrame()
        
        feedback_data = []
        with open(self.feedback_file, 'r') as f:
            for line in f:
                feedback_data.append(json.loads(line))
        
        return pd.DataFrame(feedback_data)
    
    def retrain_with_feedback(self):
        """Retrain model with feedback data"""
        logger.info("Starting retraining with feedback data...")
        
        # Load feedback
        feedback_df = self.load_feedback_data()
        
        if feedback_df.empty or len(feedback_df) < self.config['self_learning']['min_samples_for_retrain']:
            logger.warning("Not enough feedback data for retraining")
            return
        
        # Load original training data
        data_loader = DataLoader(self.config)
        original_df = data_loader.load_data(self.config['data']['dataset_path'])
        
        # Combine with feedback data
        feedback_training = feedback_df[['query', 'correct_intent']].copy()
        feedback_training.columns = ['query', 'intent']
        
        # Combine datasets
        combined_df = pd.concat([original_df, feedback_training], ignore_index=True)
        logger.info(f"Combined dataset size: {len(combined_df)}")
        
        # Prepare data
        X_train, X_test, y_train, y_test = data_loader.prepare_data(combined_df)
        
        # Train new model
        classifier = create_classifier(self.config)
        classifier.train(X_train, y_train)
        
        # Evaluate
        y_pred = classifier.predict(X_test)
        accuracy = (y_pred == y_test).mean()
        logger.info(f"Retrained model accuracy: {accuracy:.4f}")
        
        # Save retrained model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{self.config['model']['type']}_retrained_{timestamp}.pkl"
        model_path = os.path.join(
            self.config['training']['model_save_path'],
            model_filename
        )
        classifier.save_model(model_path)
        logger.info(f"Retrained model saved to {model_path}")
        
        # Save updated label encoder and intent mapping
        label_encoder_path = os.path.join(
            self.config['training']['model_save_path'],
            f"label_encoder_retrained_{timestamp}.pkl"
        )
        joblib.dump(data_loader.get_label_encoder(), label_encoder_path)
        
        intent_mapping_path = os.path.join(
            self.config['training']['model_save_path'],
            f"intent_mapping_retrained_{timestamp}.pkl"
        )
        joblib.dump(data_loader.get_intent_mapping(), intent_mapping_path)
        
        # Reset feedback counter
        self.feedback_count = 0
        
        # Archive feedback file
        archive_path = os.path.join(
            self.feedback_storage,
            f"feedback_archived_{timestamp}.jsonl"
        )
        if os.path.exists(self.feedback_file):
            os.rename(self.feedback_file, archive_path)
            logger.info(f"Feedback archived to {archive_path}")
    
    def get_feedback_statistics(self) -> Dict:
        """
        Get statistics about feedback
        
        Returns:
            Dictionary with feedback statistics
        """
        feedback_df = self.load_feedback_data()
        
        if feedback_df.empty:
            return {
                'total_feedback': 0,
                'correct_predictions': 0,
                'incorrect_predictions': 0,
                'accuracy': 0.0
            }
        
        stats = {
            'total_feedback': len(feedback_df),
            'correct_predictions': int(feedback_df['is_correct'].sum()),
            'incorrect_predictions': int((~feedback_df['is_correct']).sum()),
            'accuracy': float(feedback_df['is_correct'].mean()),
            'avg_confidence': float(feedback_df['confidence'].mean()),
            'intents_corrected': feedback_df['correct_intent'].value_counts().to_dict()
        }
        
        return stats
    
    def interactive_feedback_mode(self):
        """Interactive mode for providing feedback"""
        from inference import IntentPredictor
        
        predictor = IntentPredictor(config_path='config.yaml')
        
        print("\n" + "="*60)
        print("SELF-LEARNING SYSTEM - FEEDBACK MODE")
        print("="*60)
        print("Provide feedback to improve the model")
        print("Commands: 'stats' for statistics, 'quit' to exit")
        print("")
        
        while True:
            query = input("\nQuery: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if query.lower() == 'stats':
                stats = self.get_feedback_statistics()
                print("\n" + "-"*60)
                print("FEEDBACK STATISTICS")
                print("-"*60)
                for key, value in stats.items():
                    print(f"{key}: {value}")
                print("-"*60)
                continue
            
            if not query:
                continue
            
            # Get prediction
            result = predictor.predict(query)
            
            print("\n" + "-"*60)
            print(f"Predicted Intent: {result['predicted_intent']}")
            print(f"Confidence: {result['confidence']:.4f}")
            
            if result['is_uncertain']:
                print("⚠️  Low confidence prediction")
            
            # Ask for feedback
            feedback = input("\nIs this correct? (y/n/skip): ").strip().lower()
            
            if feedback == 'skip':
                continue
            elif feedback == 'y':
                self.add_feedback(
                    query,
                    result['predicted_intent'],
                    result['predicted_intent'],
                    result['confidence']
                )
                print("✓ Feedback recorded (correct)")
            elif feedback == 'n':
                correct_intent = input("Enter correct intent: ").strip()
                self.add_feedback(
                    query,
                    result['predicted_intent'],
                    correct_intent,
                    result['confidence']
                )
                print("✓ Feedback recorded (corrected)")
            
            print(f"\nFeedback samples collected: {self.feedback_count}")
            if self.feedback_count >= self.config['self_learning']['min_samples_for_retrain']:
                print("⚠️  Sufficient feedback for retraining!")
            print("-"*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Learning System")
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--feedback', action='store_true',
                       help='Run in interactive feedback mode')
    parser.add_argument('--retrain', action='store_true',
                       help='Retrain model with existing feedback')
    parser.add_argument('--stats', action='store_true',
                       help='Show feedback statistics')
    
    args = parser.parse_args()
    
    system = SelfLearningSystem(args.config)
    
    if args.stats:
        stats = system.get_feedback_statistics()
        print("\nFeedback Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    elif args.retrain:
        system.retrain_with_feedback()
    elif args.feedback:
        system.interactive_feedback_mode()
    else:
        print("Please specify --feedback, --retrain, or --stats")

