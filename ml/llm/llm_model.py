"""
LLM-based Intent Classification
Supports various small language models for intent detection
"""

import os
import logging
import numpy as np
from typing import Dict, List, Tuple
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMIntentClassifier:
    """LLM-based intent classifier using embeddings"""
    
    def __init__(self, config: Dict):
        """
        Initialize LLM classifier
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.llm_config = config['model']['llm']
        self.model_name = self.llm_config['model_name']
        self.device = self.llm_config.get('device', 'cpu')
        
        self.model = None
        self.intent_embeddings = None
        self.intent_names = None
        
        logger.info(f"Initializing LLM classifier with model: {self.model_name}")
        
    def load_model(self):
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, intent_mapping: Dict):
        """
        Train by creating embeddings for each intent class
        
        Args:
            X_train: Training queries
            y_train: Training labels
            intent_mapping: Mapping from labels to intent names
        """
        if self.model is None:
            self.load_model()
        
        logger.info("Training LLM classifier by creating intent embeddings...")
        
        # Store intent names
        self.intent_names = [intent_mapping[i] for i in sorted(intent_mapping.keys())]
        
        # Create embeddings for each intent by averaging examples
        intent_examples = {intent: [] for intent in self.intent_names}
        
        for query, label in zip(X_train, y_train):
            intent_name = intent_mapping[label]
            intent_examples[intent_name].append(query)
        
        # Compute average embeddings for each intent
        self.intent_embeddings = {}
        
        for intent, examples in intent_examples.items():
            if examples:
                logger.info(f"Creating embedding for {intent} ({len(examples)} examples)")
                embeddings = self.model.encode(examples)
                # Average the embeddings
                avg_embedding = np.mean(embeddings, axis=0)
                self.intent_embeddings[intent] = avg_embedding
        
        logger.info(f"Created embeddings for {len(self.intent_embeddings)} intents")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict intents using cosine similarity
        
        Args:
            X: Input queries
            
        Returns:
            Predicted intent indices
        """
        predictions = []
        
        for query in X:
            # Encode query
            query_embedding = self.model.encode([query])[0]
            
            # Calculate similarity with each intent
            similarities = {}
            for intent, intent_emb in self.intent_embeddings.items():
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    intent_emb.reshape(1, -1)
                )[0][0]
                similarities[intent] = similarity
            
            # Get best match
            best_intent = max(similarities, key=similarities.get)
            intent_idx = self.intent_names.index(best_intent)
            predictions.append(intent_idx)
        
        return np.array(predictions)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities using softmax on similarities
        
        Args:
            X: Input queries
            
        Returns:
            Probability distributions
        """
        probabilities = []
        
        for query in X:
            # Encode query
            query_embedding = self.model.encode([query])[0]
            
            # Calculate similarity with each intent
            similarities = []
            for intent in self.intent_names:
                intent_emb = self.intent_embeddings[intent]
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    intent_emb.reshape(1, -1)
                )[0][0]
                similarities.append(similarity)
            
            # Convert to probabilities using softmax with better scaling
            similarities = np.array(similarities)
            # Scale similarities more aggressively for better confidence scores
            temperature = self.llm_config.get('temperature', 0.1)  # Lower temp = more confident
            # Shift and scale to enhance differences
            scaled = (similarities - np.min(similarities))  # Make minimum 0
            if np.max(scaled) > 0:
                scaled = scaled / np.max(scaled)  # Scale to [0, 1]
            # Apply softmax with temperature
            exp_scores = np.exp(scaled / temperature)
            probs = exp_scores / np.sum(exp_scores)
            
            probabilities.append(probs)
        
        return np.array(probabilities)
    
    def save_model(self, path: str):
        """Save model and embeddings"""
        import joblib
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save embeddings and metadata
        model_data = {
            'intent_embeddings': self.intent_embeddings,
            'intent_names': self.intent_names,
            'model_name': self.model_name,
            'config': self.llm_config
        }
        
        joblib.dump(model_data, path)
        logger.info(f"LLM model data saved to {path}")
    
    def load_saved_model(self, path: str):
        """Load saved model and embeddings"""
        import joblib
        
        if self.model is None:
            self.load_model()
        
        model_data = joblib.load(path)
        self.intent_embeddings = model_data['intent_embeddings']
        self.intent_names = model_data['intent_names']
        
        logger.info(f"LLM model data loaded from {path}")


class HybridIntentClassifier:
    """Hybrid classifier combining traditional ML and LLM"""
    
    def __init__(self, config: Dict, traditional_model, llm_model):
        """
        Initialize hybrid classifier
        
        Args:
            config: Configuration dictionary
            traditional_model: Trained traditional model (SVM/RF)
            llm_model: Trained LLM model
        """
        self.config = config
        self.traditional_model = traditional_model
        self.llm_model = llm_model
        self.router_config = config['model']['router']
        
        logger.info("Initialized hybrid classifier")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict using hybrid approach
        
        Args:
            X: Input queries
            
        Returns:
            Predicted labels
        """
        # Get predictions from both models
        trad_preds = self.traditional_model.predict(X)
        trad_proba = self.traditional_model.predict_proba(X)
        
        llm_preds = self.llm_model.predict(X)
        llm_proba = self.llm_model.predict_proba(X)
        
        # Combine based on configuration
        if self.router_config.get('hybrid_mode', False):
            # Average probabilities
            combined_proba = (trad_proba + llm_proba) / 2
            predictions = np.argmax(combined_proba, axis=1)
        else:
            # Use confidence-based routing
            threshold = self.router_config.get('confidence_threshold', 0.7)
            predictions = []
            
            for i, (t_pred, t_prob) in enumerate(zip(trad_preds, trad_proba)):
                max_conf = np.max(t_prob)
                
                if max_conf < threshold:
                    # Use LLM for low-confidence predictions
                    predictions.append(llm_preds[i])
                else:
                    # Use traditional model
                    predictions.append(t_pred)
            
            predictions = np.array(predictions)
        
        return predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get hybrid probability predictions"""
        trad_proba = self.traditional_model.predict_proba(X)
        llm_proba = self.llm_model.predict_proba(X)
        
        if self.router_config.get('hybrid_mode', False):
            # Average probabilities
            return (trad_proba + llm_proba) / 2
        else:
            # Return traditional probabilities (routing happens in predict)
            return trad_proba


class ModelRouter:
    """Routes requests to appropriate model based on configuration"""
    
    def __init__(self, config: Dict):
        """
        Initialize model router
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.router_config = config['model'].get('router', {})
        self.model_type = config['model']['type']
        
        self.traditional_model = None
        self.llm_model = None
        self.active_model = None
        
        logger.info(f"Model router initialized with type: {self.model_type}")
    
    def setup_models(self, traditional_model=None, llm_model=None):
        """Setup the models for routing"""
        self.traditional_model = traditional_model
        self.llm_model = llm_model
        
        # Determine active model
        if self.model_type == 'llm':
            self.active_model = llm_model
            logger.info("Using LLM model only")
        elif self.model_type == 'hybrid':
            self.active_model = HybridIntentClassifier(
                self.config, traditional_model, llm_model
            )
            logger.info("Using hybrid model")
        else:
            self.active_model = traditional_model
            logger.info("Using traditional model only")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Route prediction to appropriate model"""
        if self.active_model is None:
            raise ValueError("Models not set up. Call setup_models() first.")
        
        return self.active_model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Route probability prediction to appropriate model"""
        if self.active_model is None:
            raise ValueError("Models not set up. Call setup_models() first.")
        
        return self.active_model.predict_proba(X)
    
    def get_model_info(self) -> Dict:
        """Get information about active models"""
        return {
            'model_type': self.model_type,
            'use_llm': self.router_config.get('use_llm', False),
            'hybrid_mode': self.router_config.get('hybrid_mode', False),
            'traditional_available': self.traditional_model is not None,
            'llm_available': self.llm_model is not None
        }


if __name__ == "__main__":
    # Test LLM classifier
    from data_loader import load_config
    
    config = load_config()
    
    # Update config to use LLM
    config['model']['type'] = 'llm'
    
    classifier = LLMIntentClassifier(config)
    print("LLM Classifier initialized successfully!")
    print(f"Using model: {classifier.model_name}")

