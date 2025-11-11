"""
Training script for Intent Classification System
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ml.data.data_loader import DataLoader, load_config
from ml.traditional_ml.model import create_classifier
from ml.traditional_ml.visualizer import IntentVisualizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_model(config_path: str = 'config.yaml'):
    """
    Train intent classification model
    
    Args:
        config_path: Path to configuration file
    """
    # Load configuration
    config = load_config(config_path)
    logger.info("Configuration loaded successfully")
    
    # Create necessary directories
    os.makedirs(config['training']['model_save_path'], exist_ok=True)
    os.makedirs(os.path.dirname(config['logging']['log_file']), exist_ok=True)
    
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
    
    # Visualize train/test split
    logger.info("Creating train/test split visualization...")
    visualizer.plot_training_split(y_train, y_test, data_loader.get_intent_mapping())
    
    # Create and train model
    logger.info("\n" + "="*60)
    logger.info("STEP 2: MODEL TRAINING")
    logger.info("="*60)
    logger.info(f"Creating {config['model']['type']} classifier...")
    classifier = create_classifier(config)
    
    logger.info("Starting model training...")
    start_time = datetime.now()
    classifier.train(X_train, y_train)
    training_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Training completed in {training_time:.2f} seconds")
    
    # Evaluate on training set
    logger.info("\n" + "="*60)
    logger.info("STEP 3: MODEL EVALUATION")
    logger.info("="*60)
    train_predictions = classifier.predict(X_train)
    train_accuracy = (train_predictions == y_train).mean()
    logger.info(f"Training accuracy: {train_accuracy:.4f}")
    
    # Evaluate on test set
    test_predictions = classifier.predict(X_test)
    test_probabilities = classifier.predict_proba(X_test)
    test_accuracy = (test_predictions == y_test).mean()
    logger.info(f"Test accuracy: {test_accuracy:.4f}")
    
    # Create comprehensive visualizations
    logger.info("\n" + "="*60)
    logger.info("STEP 4: GENERATING VISUALIZATIONS")
    logger.info("="*60)
    
    report_dir, viz_paths = visualizer.create_comprehensive_report(
        y_test, test_predictions, test_probabilities,
        data_loader.get_intent_mapping(),
        model_name=config['model']['type']
    )
    
    logger.info(f"All visualizations saved to: {report_dir}")
    
    # Save model
    logger.info("\n" + "="*60)
    logger.info("STEP 5: SAVING MODEL")
    logger.info("="*60)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"{config['model']['type']}_model_{timestamp}.pkl"
    model_path = os.path.join(config['training']['model_save_path'], model_filename)
    
    if config['model']['type'] == 'ensemble':
        model_dir = os.path.join(config['training']['model_save_path'], f"ensemble_{timestamp}")
        classifier.save_model(model_dir)
    else:
        classifier.save_model(model_path)
    
    # Save label encoder
    label_encoder_path = os.path.join(
        config['training']['model_save_path'], 
        f"label_encoder_{timestamp}.pkl"
    )
    import joblib
    joblib.dump(data_loader.get_label_encoder(), label_encoder_path)
    logger.info(f"Label encoder saved to {label_encoder_path}")
    
    # Save intent mapping
    intent_mapping_path = os.path.join(
        config['training']['model_save_path'],
        f"intent_mapping_{timestamp}.pkl"
    )
    joblib.dump(data_loader.get_intent_mapping(), intent_mapping_path)
    logger.info(f"Intent mapping saved to {intent_mapping_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print(f"Model Type: {config['model']['type']}")
    print(f"Training Samples: {len(X_train)}")
    print(f"Test Samples: {len(X_test)}")
    print(f"Number of Intents: {len(data_loader.get_intent_mapping())}")
    print(f"Training Accuracy: {train_accuracy:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"Training Time: {training_time:.2f} seconds")
    print(f"Model saved to: {model_path if config['model']['type'] != 'ensemble' else model_dir}")
    print("="*60)
    
    return classifier, data_loader, test_accuracy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Intent Classification Model")
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    train_model(args.config)

