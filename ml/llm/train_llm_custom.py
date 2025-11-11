"""
Custom LLM Training Script
Trains on datasets v1 and v2, tests on v3
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from ml.data.data_loader import DataLoader, load_config
from ml.llm.llm_model import LLMIntentClassifier
from ml.traditional_ml.visualizer import IntentVisualizer
import joblib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_multiple_datasets(data_loader, file_paths):
    """Load and combine multiple datasets"""
    all_data = []
    
    for file_path in file_paths:
        logger.info(f"Loading {file_path}...")
        df = data_loader.load_data(file_path)
        all_data.append(df)
        logger.info(f"  Loaded {len(df)} samples")
    
    # Combine all datasets
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"Total combined samples: {len(combined_df)}")
    
    return combined_df


def train_llm_with_custom_split(config_path: str = 'config.yaml'):
    """
    Train LLM using v1+v2 for training, v3 for testing
    
    Args:
        config_path: Path to configuration file
    """
    # Load configuration
    config = load_config(config_path)
    logger.info("Configuration loaded successfully")
    
    # Create necessary directories
    os.makedirs(config['training']['model_save_path'], exist_ok=True)
    os.makedirs('visualizations', exist_ok=True)
    
    # Initialize components
    visualizer = IntentVisualizer()
    data_loader = DataLoader(config)
    
    logger.info("\n" + "="*70)
    logger.info("STEP 1: DATA LOADING - Training on v1+v2, Testing on v3")
    logger.info("="*70)
    
    # Load training datasets (v1 and v2)
    train_files = [
        'ml/data/raw/infra_copilot_intent_dataset_v1_1.jsonl',
        'ml/data/raw/infra_copilot_intent_dataset_v2.jsonl'
    ]
    
    train_df = load_multiple_datasets(data_loader, train_files)
    
    # Load test dataset (v3)
    logger.info("\nLoading test dataset (v3)...")
    test_df = data_loader.load_data('ml/data/raw/infra_copilot_intent_dataset_v3.jsonl')
    
    # Visualize combined data distribution
    logger.info("\nCreating data distribution visualizations...")
    visualizer.plot_data_distribution(train_df, save_name='train_data_distribution.png')
    visualizer.plot_data_distribution(test_df, save_name='test_data_distribution.png')
    
    # Preprocess data
    logger.info("\nPreparing training data...")
    train_df['processed_query'] = train_df['query'].apply(data_loader.preprocess_text)
    test_df['processed_query'] = test_df['query'].apply(data_loader.preprocess_text)
    
    # Encode labels
    y_train_encoded = data_loader.label_encoder.fit_transform(train_df['intent'])
    
    # Filter test set to only include intents seen during training
    trained_intents = set(train_df['intent'].unique())
    test_intents = set(test_df['intent'].unique())
    
    unseen_intents = test_intents - trained_intents
    if unseen_intents:
        logger.info(f"\n⚠️  Test set contains {len(unseen_intents)} unseen intents:")
        for intent in sorted(unseen_intents):
            count = (test_df['intent'] == intent).sum()
            logger.info(f"     - {intent} ({count} samples)")
        
        logger.info(f"\n📊 Filtering test set to known intents only...")
        original_test_size = len(test_df)
        test_df = test_df[test_df['intent'].isin(trained_intents)]
        logger.info(f"     Kept {len(test_df)}/{original_test_size} test samples")
    
    # Now encode test labels
    y_test_encoded = data_loader.label_encoder.transform(test_df['intent'])
    
    # Get arrays
    X_train = train_df['processed_query'].values
    X_test = test_df['processed_query'].values
    y_train = y_train_encoded
    y_test = y_test_encoded
    
    # Create intent mapping
    data_loader.intent_mapping = dict(zip(
        data_loader.label_encoder.transform(data_loader.label_encoder.classes_),
        data_loader.label_encoder.classes_
    ))
    intent_mapping = data_loader.intent_mapping
    
    logger.info(f"\n📊 Data Split Summary:")
    logger.info(f"   Training samples: {len(X_train)} (v1 + v2)")
    logger.info(f"   Test samples: {len(X_test)} (v3)")
    logger.info(f"   Number of intents: {len(intent_mapping)}")
    logger.info(f"   Intent mapping created with {len(intent_mapping)} classes")
    
    # Visualize train/test split
    logger.info("\nCreating train/test split visualization...")
    visualizer.plot_training_split(y_train, y_test, intent_mapping, 
                                   save_name='custom_training_split.png')
    
    # Initialize and train LLM
    logger.info("\n" + "="*70)
    logger.info("STEP 2: LLM MODEL TRAINING")
    logger.info("="*70)
    
    logger.info(f"🤖 Initializing LLM: {config['model']['llm']['model_name']}")
    llm_classifier = LLMIntentClassifier(config)
    
    logger.info("Training LLM model...")
    logger.info("  This will create embeddings for all intents...")
    
    start_time = datetime.now()
    llm_classifier.train(X_train, y_train, intent_mapping)
    training_time = (datetime.now() - start_time).total_seconds()
    
    logger.info(f"✅ Training completed in {training_time:.2f} seconds")
    
    # Evaluate model
    logger.info("\n" + "="*70)
    logger.info("STEP 3: MODEL EVALUATION")
    logger.info("="*70)
    
    # Training set evaluation
    logger.info("Evaluating on training set...")
    train_preds = llm_classifier.predict(X_train)
    train_proba = llm_classifier.predict_proba(X_train)
    train_accuracy = (train_preds == y_train).mean()
    
    # Test set evaluation
    logger.info("Evaluating on test set (v3)...")
    test_preds = llm_classifier.predict(X_test)
    test_proba = llm_classifier.predict_proba(X_test)
    test_accuracy = (test_preds == y_test).mean()
    
    logger.info(f"\n📈 Performance Metrics:")
    logger.info(f"   Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    logger.info(f"   Test Accuracy (v3): {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    
    # Calculate confidence statistics
    test_confidences = np.max(test_proba, axis=1)
    logger.info(f"\n🎯 Confidence Statistics (Test Set):")
    logger.info(f"   Average Confidence: {np.mean(test_confidences):.4f}")
    logger.info(f"   Min Confidence: {np.min(test_confidences):.4f}")
    logger.info(f"   Max Confidence: {np.max(test_confidences):.4f}")
    logger.info(f"   Std Confidence: {np.std(test_confidences):.4f}")
    
    high_conf_threshold = 0.7
    high_conf_mask = test_confidences >= high_conf_threshold
    if high_conf_mask.sum() > 0:
        high_conf_acc = (test_preds[high_conf_mask] == y_test[high_conf_mask]).mean()
        logger.info(f"   High Confidence (≥{high_conf_threshold}) Accuracy: {high_conf_acc:.4f}")
        logger.info(f"   High Confidence Samples: {high_conf_mask.sum()}/{len(test_confidences)}")
    
    # Create visualizations
    logger.info("\n" + "="*70)
    logger.info("STEP 4: GENERATING VISUALIZATIONS")
    logger.info("="*70)
    
    report_dir, viz_paths = visualizer.create_comprehensive_report(
        y_test, test_preds, test_proba,
        intent_mapping,
        model_name='llm_custom'
    )
    
    logger.info(f"✅ All visualizations saved to: {report_dir}")
    
    # Save models
    logger.info("\n" + "="*70)
    logger.info("STEP 5: SAVING MODEL AND ARTIFACTS")
    logger.info("="*70)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save LLM model
    llm_model_path = os.path.join(
        config['training']['model_save_path'],
        f"llm_model_{timestamp}.pkl"
    )
    llm_classifier.save_model(llm_model_path)
    logger.info(f"✅ LLM model saved to: {llm_model_path}")
    
    # Save label encoder
    label_encoder_path = os.path.join(
        config['training']['model_save_path'],
        f"llm_label_encoder_{timestamp}.pkl"
    )
    joblib.dump(data_loader.get_label_encoder(), label_encoder_path)
    logger.info(f"✅ Label encoder saved to: {label_encoder_path}")
    
    # Save intent mapping
    intent_mapping_path = os.path.join(
        config['training']['model_save_path'],
        f"llm_intent_mapping_{timestamp}.pkl"
    )
    joblib.dump(intent_mapping, intent_mapping_path)
    logger.info(f"✅ Intent mapping saved to: {intent_mapping_path}")
    
    # Save training metadata
    metadata = {
        'model_type': 'llm',
        'llm_model_name': config['model']['llm']['model_name'],
        'training_files': train_files,
        'test_file': 'infra_copilot_intent_dataset_v3.jsonl',
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'num_intents': len(intent_mapping),
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'avg_confidence': float(np.mean(test_confidences)),
        'training_time_seconds': training_time,
        'timestamp': timestamp,
        'intent_names': list(intent_mapping.values())
    }
    
    metadata_path = os.path.join(
        config['training']['model_save_path'],
        f"llm_metadata_{timestamp}.pkl"
    )
    joblib.dump(metadata, metadata_path)
    logger.info(f"✅ Training metadata saved to: {metadata_path}")
    
    # Print final summary
    print("\n" + "="*70)
    print("🎉 TRAINING COMPLETE!")
    print("="*70)
    print(f"📦 Model Type: LLM (Sentence Transformers)")
    print(f"🤖 LLM Model: {config['model']['llm']['model_name']}")
    print(f"📚 Training Data: v1 + v2 ({len(X_train)} samples)")
    print(f"🧪 Test Data: v3 ({len(X_test)} samples)")
    print(f"🎯 Number of Intents: {len(intent_mapping)}")
    print(f"")
    print(f"📊 Results:")
    print(f"   Training Accuracy:  {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    print(f"   Test Accuracy (v3): {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
    print(f"   Avg Confidence:     {np.mean(test_confidences):.4f} ({np.mean(test_confidences)*100:.2f}%)")
    print(f"")
    print(f"⏱️  Training Time: {training_time:.2f} seconds")
    print(f"💾 Model saved to: {llm_model_path}")
    print(f"📈 Visualizations: {report_dir}")
    print("="*70)
    print(f"\n✨ Next steps:")
    print(f"   1. Check visualizations in: {report_dir}")
    print(f"   2. Update web_app.py to use LLM model")
    print(f"   3. Restart web app: pkill -f web_app.py && python web_app.py")
    print(f"   4. Test at: http://localhost:5000")
    print("="*70 + "\n")
    
    return llm_classifier, data_loader, metadata


if __name__ == "__main__":
    train_llm_with_custom_split()

