"""
Model definitions for Intent Classification System
Supports multiple model architectures
"""

import os
import logging
import numpy as np
from typing import Dict, Tuple, List
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.calibration import CalibratedClassifierCV

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentClassifier:
    """Base class for intent classification models"""
    
    def __init__(self, config: Dict):
        """
        Initialize classifier with configuration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.model = None
        self.model_type = config['model']['type']
        
    def build_model(self):
        """Build the classification model"""
        raise NotImplementedError
        
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the model"""
        raise NotImplementedError
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        raise NotImplementedError
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        raise NotImplementedError
        
    def save_model(self, path: str):
        """Save model to disk"""
        raise NotImplementedError
        
    def load_model(self, path: str):
        """Load model from disk"""
        raise NotImplementedError


class TfidfSVMClassifier(IntentClassifier):
    """TF-IDF + SVM based classifier"""
    
    def build_model(self):
        """Build TF-IDF + SVM pipeline"""
        logger.info("Building TF-IDF + SVM model")
        
        tfidf_config = self.config['model']['tfidf']
        svm_config = self.config['model']['svm']
        
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=tfidf_config['max_features'],
                ngram_range=tuple(tfidf_config['ngram_range']),
                min_df=tfidf_config['min_df'],
                max_df=tfidf_config['max_df'],
                use_idf=tfidf_config['use_idf'],
                sublinear_tf=tfidf_config['sublinear_tf']
            )),
            ('svm', SVC(
                kernel=svm_config['kernel'],
                C=svm_config['C'],
                probability=svm_config['probability'],
                class_weight=svm_config['class_weight'],
                random_state=self.config['data']['random_seed']
            ))
        ])
        
        return self.model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train the SVM model with optional calibration
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        logger.info("Training TF-IDF + SVM model")
        
        if self.model is None:
            self.build_model()
        
        # Perform cross-validation
        if self.config['training']['cross_validation_folds'] > 1:
            cv_scores = cross_val_score(
                self.model, X_train, y_train,
                cv=self.config['training']['cross_validation_folds'],
                scoring='accuracy'
            )
            logger.info(f"Cross-validation scores: {cv_scores}")
            logger.info(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Train final model
        self.model.fit(X_train, y_train)
        
        # Apply probability calibration if enabled
        if self.config['model'].get('calibration', {}).get('enabled', False):
            logger.info("Applying probability calibration...")
            calibration_config = self.config['model']['calibration']
            
            calibrated_model = CalibratedClassifierCV(
                self.model,
                method=calibration_config.get('method', 'sigmoid'),
                cv=calibration_config.get('cv', 3)
            )
            
            calibrated_model.fit(X_train, y_train)
            self.model = calibrated_model
            logger.info("Probability calibration completed")
        
        logger.info("Model training completed")
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input features
            
        Returns:
            Predicted labels
        """
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get prediction probabilities
        
        Args:
            X: Input features
            
        Returns:
            Prediction probabilities
        """
        return self.model.predict_proba(X)
    
    def save_model(self, path: str):
        """
        Save model to disk
        
        Args:
            path: Path to save model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """
        Load model from disk
        
        Args:
            path: Path to model file
        """
        self.model = joblib.load(path)
        logger.info(f"Model loaded from {path}")


class TfidfRandomForestClassifier(IntentClassifier):
    """TF-IDF + Random Forest based classifier"""
    
    def build_model(self):
        """Build TF-IDF + Random Forest pipeline"""
        logger.info("Building TF-IDF + Random Forest model")
        
        tfidf_config = self.config['model']['tfidf']
        rf_config = self.config['model']['random_forest']
        
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=tfidf_config['max_features'],
                ngram_range=tuple(tfidf_config['ngram_range']),
                min_df=tfidf_config['min_df'],
                max_df=tfidf_config['max_df'],
                use_idf=tfidf_config['use_idf'],
                sublinear_tf=tfidf_config['sublinear_tf']
            )),
            ('rf', RandomForestClassifier(
                n_estimators=rf_config['n_estimators'],
                max_depth=rf_config['max_depth'],
                min_samples_split=rf_config['min_samples_split'],
                min_samples_leaf=rf_config['min_samples_leaf'],
                class_weight=rf_config['class_weight'],
                random_state=self.config['data']['random_seed'],
                n_jobs=-1
            ))
        ])
        
        return self.model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the Random Forest model"""
        logger.info("Training TF-IDF + Random Forest model")
        
        if self.model is None:
            self.build_model()
        
        # Perform cross-validation
        if self.config['training']['cross_validation_folds'] > 1:
            cv_scores = cross_val_score(
                self.model, X_train, y_train,
                cv=self.config['training']['cross_validation_folds'],
                scoring='accuracy'
            )
            logger.info(f"Cross-validation scores: {cv_scores}")
            logger.info(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Train final model
        self.model.fit(X_train, y_train)
        logger.info("Model training completed")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        return self.model.predict_proba(X)
    
    def save_model(self, path: str):
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model from disk"""
        self.model = joblib.load(path)
        logger.info(f"Model loaded from {path}")


class EnsembleClassifier(IntentClassifier):
    """Ensemble of multiple classifiers"""
    
    def __init__(self, config: Dict):
        """Initialize ensemble classifier"""
        super().__init__(config)
        self.models = []
        
    def build_model(self):
        """Build ensemble of models"""
        logger.info("Building Ensemble model")
        
        # Create SVM model
        svm_classifier = TfidfSVMClassifier(self.config)
        svm_classifier.build_model()
        self.models.append(('svm', svm_classifier))
        
        # Create Random Forest model
        rf_classifier = TfidfRandomForestClassifier(self.config)
        rf_classifier.build_model()
        self.models.append(('rf', rf_classifier))
        
        return self.models
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train all models in ensemble"""
        logger.info("Training Ensemble models")
        
        if not self.models:
            self.build_model()
        
        for name, model in self.models:
            logger.info(f"Training {name} model")
            model.train(X_train, y_train)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using voting"""
        predictions = []
        
        for name, model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Majority voting
        predictions = np.array(predictions)
        final_predictions = np.apply_along_axis(
            lambda x: np.bincount(x).argmax(), 
            axis=0, 
            arr=predictions
        )
        
        return final_predictions
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get averaged prediction probabilities"""
        probas = []
        
        for name, model in self.models:
            proba = model.predict_proba(X)
            probas.append(proba)
        
        # Average probabilities
        avg_proba = np.mean(probas, axis=0)
        return avg_proba
    
    def save_model(self, path: str):
        """Save all models in ensemble"""
        os.makedirs(path, exist_ok=True)
        
        for name, model in self.models:
            model_path = os.path.join(path, f"{name}_model.pkl")
            model.save_model(model_path)
        
        logger.info(f"Ensemble models saved to {path}")
    
    def load_model(self, path: str):
        """Load all models in ensemble"""
        self.models = []
        
        # Load SVM
        svm_classifier = TfidfSVMClassifier(self.config)
        svm_classifier.load_model(os.path.join(path, "svm_model.pkl"))
        self.models.append(('svm', svm_classifier))
        
        # Load Random Forest
        rf_classifier = TfidfRandomForestClassifier(self.config)
        rf_classifier.load_model(os.path.join(path, "rf_model.pkl"))
        self.models.append(('rf', rf_classifier))
        
        logger.info(f"Ensemble models loaded from {path}")


def create_classifier(config: Dict) -> IntentClassifier:
    """
    Factory function to create classifier based on config
    
    Args:
        config: Configuration dictionary
        
    Returns:
        IntentClassifier instance
    """
    model_type = config['model']['type']
    
    if model_type == 'tfidf_svm':
        return TfidfSVMClassifier(config)
    elif model_type == 'tfidf_rf':
        return TfidfRandomForestClassifier(config)
    elif model_type == 'ensemble':
        return EnsembleClassifier(config)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


if __name__ == "__main__":
    from data_loader import load_config
    
    config = load_config()
    classifier = create_classifier(config)
    print(f"Created classifier: {type(classifier).__name__}")

