"""
Training script for LLM-based Intent Classification
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import joblib

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.data.data_loader import DataLoader, load_config
from ml.llm.llm_model import LLMIntentClassifier, ModelRouter
from ml.traditional_ml.model import create_classifier
from ml.traditional_ml.visualizer import IntentVisualizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_llm_model(config_path: str = 'config.yaml', use_hybrid: bool = False):
    """
    Train LLM-based intent classification model
    
    Args:
        config_path: Path to configuration file
        use_hybrid: Whether to train hybrid model (traditional + LLM)
    """
    # Load configuration
    config = load_config(config_path)
    logger.info("Configuration loaded successfully")
    
    # Create necessary directories
    os.makedirs(config['training']['model_save_path'], exist_ok=True)
    
    # Initialize visualizer
    visualizer = IntentVisualizer()
    logger.info("="*60)
    logger.info("STEP 1: DATA LOADING AND ANALYSIS")
    logger.info("="*60)
    
    # Load and prepare data
    logger.info("Loading and preparing data...")
    data_loader = DataLoader(config)
    df = data_loader.load_data(config['data']['dataset_path'])
    
    # Visualize data distribution
    logger.info("Creating data distribution visualizations...")
    visualizer.plot_data_distribution(df)
    
    X_train, X_test, y_train, y_test = data_loader.prepare_data(df)
    intent_mapping = data_loader.get_intent_mapping()
    
    # Visualize train/test split
    logger.info("Creating train/test split visualization...")
    visualizer.plot_training_split(y_train, y_test, intent_mapping)
    
    logger.info("\n" + "="*60)
    logger.info("STEP 2: LLM MODEL TRAINING")
    logger.info("="*60)
    
    # Train LLM model
    logger.info("Creating LLM classifier...")
    llm_classifier = LLMIntentClassifier(config)
    
    logger.info("Training LLM model...")
    start_time = datetime.now()
    llm_classifier.train(X_train, y_train, intent_mapping)
    training_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"LLM training completed in {training_time:.2f} seconds")
    
    # Evaluate LLM model
    logger.info("\n" + "="*60)
    logger.info("STEP 3: MODEL EVALUATION")
    logger.info("="*60)
    
    llm_train_preds = llm_classifier.predict(X_train)
    llm_train_accuracy = (llm_train_preds == y_train).mean()
    logger.info(f"LLM Training accuracy: {llm_train_accuracy:.4f}")
    
    llm_test_preds = llm_classifier.predict(X_test)
    llm_test_proba = llm_classifier.predict_proba(X_test)
    llm_test_accuracy = (llm_test_preds == y_test).mean()
    logger.info(f"LLM Test accuracy: {llm_test_accuracy:.4f}")
    
    # Train hybrid model if requested
    if use_hybrid:
        logger.info("\n" + "="*60)
        logger.info("STEP 4: HYBRID MODEL TRAINING")
        logger.info("="*60)
        
        # Train traditional model
        logger.info("Training traditional model for hybrid approach...")
        traditional_classifier = create_classifier(config)
        traditional_classifier.train(X_train, y_train)
        
        # Evaluate hybrid
        from llm_model import HybridIntentClassifier
        hybrid_classifier = HybridIntentClassifier(
            config, traditional_classifier, llm_classifier
        )
        
        hybrid_test_preds = hybrid_classifier.predict(X_test)
        hybrid_test_accuracy = (hybrid_test_preds == y_test).mean()
        logger.info(f"Hybrid Test accuracy: {hybrid_test_accuracy:.4f}")
    
    # Create visualizations
    logger.info("\n" + "="*60)
    logger.info("STEP 5: GENERATING VISUALIZATIONS")
    logger.info("="*60)
    
    report_dir, viz_paths = visualizer.create_comprehensive_report(
        y_test, llm_test_preds, llm_test_proba,
        intent_mapping,
        model_name='llm'
    )
    
    logger.info(f"All visualizations saved to: {report_dir}")
    
    # Save models
    logger.info("\n" + "="*60)
    logger.info("STEP 6: SAVING MODELS")
    logger.info("="*60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save LLM model
    llm_model_path = os.path.join(
        config['training']['model_save_path'],
        f"llm_model_{timestamp}.pkl"
    )
    llm_classifier.save_model(llm_model_path)
    
    # Save hybrid if used
    if use_hybrid:
        hybrid_model_dir = os.path.join(
            config['training']['model_save_path'],
            f"hybrid_{timestamp}"
        )
        os.makedirs(hybrid_model_dir, exist_ok=True)
        
        llm_classifier.save_model(os.path.join(hybrid_model_dir, "llm_model.pkl"))
        traditional_classifier.save_model(os.path.join(hybrid_model_dir, "traditional_model.pkl"))
    
    # Save metadata
    label_encoder_path = os.path.join(
        config['training']['model_save_path'],
        f"label_encoder_{timestamp}.pkl"
    )
    joblib.dump(data_loader.get_label_encoder(), label_encoder_path)
    
    intent_mapping_path = os.path.join(
        config['training']['model_save_path'],
        f"intent_mapping_{timestamp}.pkl"
    )
    joblib.dump(intent_mapping, intent_mapping_path)
    
    # Print summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Model Type: LLM (Sentence Transformers)")
    print(f"LLM Model: {config['model']['llm']['model_name']}")
    print(f"Training Samples: {len(X_train)}")
    print(f"Test Samples: {len(X_test)}")
    print(f"Number of Intents: {len(intent_mapping)}")
    print(f"LLM Training Accuracy: {llm_train_accuracy:.4f}")
    print(f"LLM Test Accuracy: {llm_test_accuracy:.4f}")
    if use_hybrid:
        print(f"Hybrid Test Accuracy: {hybrid_test_accuracy:.4f}")
    print(f"Training Time: {training_time:.2f} seconds")
    print(f"Model saved to: {llm_model_path}")
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train LLM Intent Classification Model")
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--hybrid',
        action='store_true',
        help='Train hybrid model (traditional + LLM)'
    )
    
    args = parser.parse_args()
    train_llm_model(args.config, args.hybrid)

