"""
Evaluation script for Intent Classification System
"""

import os
import logging
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from datetime import datetime
from ml.data.data_loader import DataLoader, load_config
from ml.traditional_ml.model import create_classifier
import joblib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Comprehensive model evaluation"""
    
    def __init__(self, config: dict):
        """Initialize evaluator with configuration"""
        self.config = config
        
    def evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray, 
                      y_proba: np.ndarray, intent_mapping: dict) -> dict:
        """
        Evaluate model performance
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities
            intent_mapping: Mapping from encoded labels to intent names
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating model performance...")
        
        results = {}
        
        # Overall metrics
        results['accuracy'] = accuracy_score(y_true, y_pred)
        results['precision_macro'] = precision_score(y_true, y_pred, average='macro', zero_division=0)
        results['recall_macro'] = recall_score(y_true, y_pred, average='macro', zero_division=0)
        results['f1_macro'] = f1_score(y_true, y_pred, average='macro', zero_division=0)
        
        results['precision_weighted'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        results['recall_weighted'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        results['f1_weighted'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Per-class metrics
        intent_names = [intent_mapping[i] for i in sorted(intent_mapping.keys())]
        results['classification_report'] = classification_report(
            y_true, y_pred,
            target_names=intent_names,
            zero_division=0
        )
        
        # Confusion matrix
        results['confusion_matrix'] = confusion_matrix(y_true, y_pred)
        
        # Confidence statistics
        max_probas = np.max(y_proba, axis=1)
        results['avg_confidence'] = np.mean(max_probas)
        results['min_confidence'] = np.min(max_probas)
        results['max_confidence'] = np.max(max_probas)
        results['std_confidence'] = np.std(max_probas)
        
        # Predictions by confidence level
        high_conf = max_probas >= self.config['inference']['min_confidence_threshold']
        results['high_confidence_ratio'] = np.mean(high_conf)
        results['high_confidence_accuracy'] = accuracy_score(
            y_true[high_conf], y_pred[high_conf]
        ) if np.sum(high_conf) > 0 else 0.0
        
        return results
    
    def plot_confusion_matrix(self, cm: np.ndarray, intent_mapping: dict, 
                            save_path: str = None):
        """
        Plot confusion matrix
        
        Args:
            cm: Confusion matrix
            intent_mapping: Mapping from encoded labels to intent names
            save_path: Path to save plot
        """
        intent_names = [intent_mapping[i] for i in sorted(intent_mapping.keys())]
        
        plt.figure(figsize=(16, 14))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=intent_names,
            yticklabels=intent_names,
            cbar_kws={'label': 'Count'}
        )
        plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
        plt.ylabel('True Intent', fontsize=12)
        plt.xlabel('Predicted Intent', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_confidence_distribution(self, y_proba: np.ndarray, 
                                    save_path: str = None):
        """
        Plot confidence distribution
        
        Args:
            y_proba: Prediction probabilities
            save_path: Path to save plot
        """
        max_probas = np.max(y_proba, axis=1)
        
        plt.figure(figsize=(10, 6))
        plt.hist(max_probas, bins=50, edgecolor='black', alpha=0.7)
        plt.axvline(
            self.config['inference']['min_confidence_threshold'],
            color='red', linestyle='--', linewidth=2,
            label=f"Threshold ({self.config['inference']['min_confidence_threshold']})"
        )
        plt.xlabel('Confidence Score', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Prediction Confidence Distribution', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confidence distribution saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def generate_report(self, results: dict, save_path: str = None):
        """
        Generate evaluation report
        
        Args:
            results: Evaluation results dictionary
            save_path: Path to save report
        """
        report = []
        report.append("="*80)
        report.append("INTENT CLASSIFICATION MODEL - EVALUATION REPORT")
        report.append("="*80)
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("OVERALL METRICS")
        report.append("-"*80)
        report.append(f"Accuracy:              {results['accuracy']:.4f}")
        report.append(f"Precision (Macro):     {results['precision_macro']:.4f}")
        report.append(f"Recall (Macro):        {results['recall_macro']:.4f}")
        report.append(f"F1 Score (Macro):      {results['f1_macro']:.4f}")
        report.append("")
        report.append(f"Precision (Weighted):  {results['precision_weighted']:.4f}")
        report.append(f"Recall (Weighted):     {results['recall_weighted']:.4f}")
        report.append(f"F1 Score (Weighted):   {results['f1_weighted']:.4f}")
        report.append("")
        
        report.append("CONFIDENCE STATISTICS")
        report.append("-"*80)
        report.append(f"Average Confidence:    {results['avg_confidence']:.4f}")
        report.append(f"Min Confidence:        {results['min_confidence']:.4f}")
        report.append(f"Max Confidence:        {results['max_confidence']:.4f}")
        report.append(f"Std Confidence:        {results['std_confidence']:.4f}")
        report.append(f"High Confidence Ratio: {results['high_confidence_ratio']:.4f}")
        report.append(f"High Conf. Accuracy:   {results['high_confidence_accuracy']:.4f}")
        report.append("")
        
        report.append("PER-CLASS METRICS")
        report.append("-"*80)
        report.append(results['classification_report'])
        report.append("")
        
        report.append("="*80)
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)
            logger.info(f"Evaluation report saved to {save_path}")
        
        print(report_text)
        
        return report_text


def evaluate_saved_model(config_path: str = 'config.yaml', 
                        model_path: str = None,
                        label_encoder_path: str = None,
                        intent_mapping_path: str = None):
    """
    Evaluate a saved model
    
    Args:
        config_path: Path to configuration file
        model_path: Path to saved model
        label_encoder_path: Path to label encoder
        intent_mapping_path: Path to intent mapping
    """
    # Load configuration
    config = load_config(config_path)
    logger.info("Configuration loaded successfully")
    
    # Create directories
    os.makedirs(config['evaluation']['report_path'], exist_ok=True)
    
    # Load data
    logger.info("Loading and preparing data...")
    data_loader = DataLoader(config)
    df = data_loader.load_data(config['data']['dataset_path'])
    X_train, X_test, y_train, y_test = data_loader.prepare_data(df)
    
    # Load model
    logger.info("Loading model...")
    classifier = create_classifier(config)
    
    if model_path:
        if config['model']['type'] == 'ensemble':
            classifier.load_model(model_path)
        else:
            classifier.load_model(model_path)
    else:
        # Find latest model
        model_dir = config['training']['model_save_path']
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl') and 'model' in f]
        if not model_files:
            raise FileNotFoundError("No model files found")
        latest_model = max(model_files, key=lambda x: os.path.getctime(os.path.join(model_dir, x)))
        model_path = os.path.join(model_dir, latest_model)
        classifier.load_model(model_path)
    
    logger.info(f"Model loaded from {model_path}")
    
    # Load intent mapping
    if intent_mapping_path:
        intent_mapping = joblib.load(intent_mapping_path)
    else:
        intent_mapping = data_loader.get_intent_mapping()
    
    # Make predictions
    logger.info("Making predictions...")
    y_pred = classifier.predict(X_test)
    y_proba = classifier.predict_proba(X_test)
    
    # Evaluate
    evaluator = ModelEvaluator(config)
    results = evaluator.evaluate_model(y_test, y_pred, y_proba, intent_mapping)
    
    # Generate visualizations
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    cm_path = os.path.join(
        config['evaluation']['report_path'],
        f"confusion_matrix_{timestamp}.png"
    )
    evaluator.plot_confusion_matrix(results['confusion_matrix'], intent_mapping, cm_path)
    
    conf_dist_path = os.path.join(
        config['evaluation']['report_path'],
        f"confidence_distribution_{timestamp}.png"
    )
    evaluator.plot_confidence_distribution(y_proba, conf_dist_path)
    
    # Generate report
    report_path = os.path.join(
        config['evaluation']['report_path'],
        f"evaluation_report_{timestamp}.txt"
    )
    evaluator.generate_report(results, report_path)
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Intent Classification Model")
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to model file')
    parser.add_argument('--label-encoder', type=str, default=None,
                       help='Path to label encoder file')
    parser.add_argument('--intent-mapping', type=str, default=None,
                       help='Path to intent mapping file')
    
    args = parser.parse_args()
    evaluate_saved_model(args.config, args.model, args.label_encoder, args.intent_mapping)

