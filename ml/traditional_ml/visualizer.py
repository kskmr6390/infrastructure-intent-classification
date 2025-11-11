"""
Comprehensive Visualization Module for Intent Classification System
Provides visualizations for data analysis, training, and evaluation
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from datetime import datetime
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class IntentVisualizer:
    """Comprehensive visualization for intent classification"""
    
    def __init__(self, output_dir: str = 'visualizations'):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Visualizer initialized. Outputs will be saved to {output_dir}")
    
    def plot_data_distribution(self, df: pd.DataFrame, save_name: str = 'data_distribution.png'):
        """
        Plot distribution of intents in dataset
        
        Args:
            df: DataFrame with 'intent' column
            save_name: Filename to save plot
        """
        logger.info("Creating data distribution plot...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Bar chart of intent counts
        intent_counts = df['intent'].value_counts()
        ax1 = axes[0, 0]
        intent_counts.plot(kind='bar', ax=ax1, color='steelblue')
        ax1.set_title('Intent Distribution (Count)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Intent', fontsize=12)
        ax1.set_ylabel('Count', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for i, v in enumerate(intent_counts):
            ax1.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
        
        # 2. Pie chart of intent percentages
        ax2 = axes[0, 1]
        colors = plt.cm.Set3(range(len(intent_counts)))
        intent_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Intent Distribution (Percentage)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('')
        
        # 3. Query length distribution
        ax3 = axes[1, 0]
        df['query_length'] = df['query'].str.len()
        df.boxplot(column='query_length', by='intent', ax=ax3)
        ax3.set_title('Query Length Distribution by Intent', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Intent', fontsize=12)
        ax3.set_ylabel('Query Length (characters)', fontsize=12)
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # 4. Word count distribution
        ax4 = axes[1, 1]
        df['word_count'] = df['query'].str.split().str.len()
        df.boxplot(column='word_count', by='intent', ax=ax4)
        ax4.set_title('Word Count Distribution by Intent', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Intent', fontsize=12)
        ax4.set_ylabel('Word Count', fontsize=12)
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Data distribution plot saved to {save_path}")
        plt.close()
        
        return save_path
    
    def plot_training_split(self, y_train: np.ndarray, y_test: np.ndarray, 
                           intent_mapping: dict, save_name: str = 'training_split.png'):
        """
        Visualize train/test split distribution
        
        Args:
            y_train: Training labels
            y_test: Test labels
            intent_mapping: Mapping from encoded labels to intent names
            save_name: Filename to save plot
        """
        logger.info("Creating training split visualization...")
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Get intent names
        train_intents = [intent_mapping[y] for y in y_train]
        test_intents = [intent_mapping[y] for y in y_test]
        
        train_counts = Counter(train_intents)
        test_counts = Counter(test_intents)
        
        # Prepare data
        all_intents = sorted(set(train_intents + test_intents))
        train_values = [train_counts.get(intent, 0) for intent in all_intents]
        test_values = [test_counts.get(intent, 0) for intent in all_intents]
        
        x = np.arange(len(all_intents))
        width = 0.35
        
        # Plot 1: Side-by-side bars
        ax1 = axes[0]
        bars1 = ax1.bar(x - width/2, train_values, width, label='Train', color='steelblue')
        bars2 = ax1.bar(x + width/2, test_values, width, label='Test', color='coral')
        
        ax1.set_xlabel('Intent', fontsize=12)
        ax1.set_ylabel('Count', fontsize=12)
        ax1.set_title('Train/Test Split Distribution', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(all_intents, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        # Plot 2: Stacked bar showing percentages
        ax2 = axes[1]
        total_values = [t + te for t, te in zip(train_values, test_values)]
        train_pct = [t/tot*100 if tot > 0 else 0 for t, tot in zip(train_values, total_values)]
        test_pct = [te/tot*100 if tot > 0 else 0 for te, tot in zip(test_values, total_values)]
        
        ax2.bar(x, train_pct, width*2, label='Train %', color='steelblue')
        ax2.bar(x, test_pct, width*2, bottom=train_pct, label='Test %', color='coral')
        
        ax2.set_xlabel('Intent', fontsize=12)
        ax2.set_ylabel('Percentage', fontsize=12)
        ax2.set_title('Train/Test Split Percentage', fontsize=14, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(all_intents, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Training split plot saved to {save_path}")
        plt.close()
        
        return save_path
    
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray,
                             intent_mapping: dict, normalize: bool = False,
                             save_name: str = 'confusion_matrix.png'):
        """
        Plot confusion matrix
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            intent_mapping: Mapping from encoded labels to intent names
            normalize: Whether to normalize values
            save_name: Filename to save plot
        """
        logger.info("Creating confusion matrix...")
        
        cm = confusion_matrix(y_true, y_pred)
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            fmt = '.2f'
            title = 'Normalized Confusion Matrix'
        else:
            fmt = 'd'
            title = 'Confusion Matrix'
        
        intent_names = [intent_mapping[i] for i in sorted(intent_mapping.keys())]
        
        fig, ax = plt.subplots(figsize=(16, 14))
        
        sns.heatmap(cm, annot=True, fmt=fmt, cmap='Blues', 
                   xticklabels=intent_names, yticklabels=intent_names,
                   cbar_kws={'label': 'Normalized Count' if normalize else 'Count'},
                   ax=ax, square=True, linewidths=0.5)
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('True Intent', fontsize=14)
        ax.set_xlabel('Predicted Intent', fontsize=14)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        plt.setp(ax.yaxis.get_majorticklabels(), rotation=0)
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Confusion matrix saved to {save_path}")
        plt.close()
        
        return save_path
    
    def plot_classification_metrics(self, y_true: np.ndarray, y_pred: np.ndarray,
                                   y_proba: np.ndarray, intent_mapping: dict,
                                   save_name: str = 'classification_metrics.png'):
        """
        Plot comprehensive classification metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities
            intent_mapping: Mapping from encoded labels to intent names
            save_name: Filename to save plot
        """
        logger.info("Creating classification metrics visualization...")
        
        from sklearn.metrics import precision_recall_fscore_support
        
        # Get unique labels present in y_true
        unique_labels = np.unique(y_true)
        
        # Calculate metrics per class only for labels present in test set
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, labels=unique_labels, average=None, zero_division=0
        )
        
        # Get intent names only for labels in test set
        intent_names = [intent_mapping[int(i)] for i in unique_labels]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Precision, Recall, F1 bar chart
        ax1 = axes[0, 0]
        x = np.arange(len(intent_names))
        width = 0.25
        
        ax1.bar(x - width, precision, width, label='Precision', color='steelblue')
        ax1.bar(x, recall, width, label='Recall', color='coral')
        ax1.bar(x + width, f1, width, label='F1-Score', color='lightgreen')
        
        ax1.set_xlabel('Intent', fontsize=12)
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_title('Per-Class Metrics', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(intent_names, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_ylim([0, 1.1])
        
        # 2. Support (samples per class)
        ax2 = axes[0, 1]
        bars = ax2.bar(intent_names, support, color='purple', alpha=0.7)
        ax2.set_xlabel('Intent', fontsize=12)
        ax2.set_ylabel('Number of Samples', fontsize=12)
        ax2.set_title('Test Set Distribution', fontsize=14, fontweight='bold')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        # 3. Confidence distribution
        ax3 = axes[1, 0]
        max_probas = np.max(y_proba, axis=1)
        correct = (y_true == y_pred)
        
        ax3.hist(max_probas[correct], bins=30, alpha=0.6, label='Correct', color='green', edgecolor='black')
        ax3.hist(max_probas[~correct], bins=30, alpha=0.6, label='Incorrect', color='red', edgecolor='black')
        ax3.set_xlabel('Confidence Score', fontsize=12)
        ax3.set_ylabel('Frequency', fontsize=12)
        ax3.set_title('Confidence Distribution by Correctness', fontsize=14, fontweight='bold')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Accuracy by confidence threshold
        ax4 = axes[1, 1]
        thresholds = np.linspace(0, 1, 50)
        accuracies = []
        sample_counts = []
        
        for thresh in thresholds:
            mask = max_probas >= thresh
            if mask.sum() > 0:
                acc = (y_true[mask] == y_pred[mask]).mean()
                accuracies.append(acc)
                sample_counts.append(mask.sum())
            else:
                accuracies.append(0)
                sample_counts.append(0)
        
        ax4_twin = ax4.twinx()
        
        line1 = ax4.plot(thresholds, accuracies, 'b-', linewidth=2, label='Accuracy')
        line2 = ax4_twin.plot(thresholds, sample_counts, 'r--', linewidth=2, label='Sample Count')
        
        ax4.set_xlabel('Confidence Threshold', fontsize=12)
        ax4.set_ylabel('Accuracy', fontsize=12, color='b')
        ax4_twin.set_ylabel('Sample Count', fontsize=12, color='r')
        ax4.set_title('Accuracy vs Confidence Threshold', fontsize=14, fontweight='bold')
        ax4.tick_params(axis='y', labelcolor='b')
        ax4_twin.tick_params(axis='y', labelcolor='r')
        ax4.grid(alpha=0.3)
        
        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax4.legend(lines, labels, loc='best')
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Classification metrics plot saved to {save_path}")
        plt.close()
        
        return save_path
    
    def plot_feature_importance(self, model, feature_names: list = None,
                               top_n: int = 30, save_name: str = 'feature_importance.png'):
        """
        Plot feature importance for tree-based models
        
        Args:
            model: Trained model with feature_importances_
            feature_names: List of feature names
            top_n: Number of top features to show
            save_name: Filename to save plot
        """
        logger.info("Creating feature importance plot...")
        
        try:
            # Get feature importance
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            elif hasattr(model, 'named_steps') and hasattr(model.named_steps[list(model.named_steps.keys())[-1]], 'feature_importances_'):
                importances = model.named_steps[list(model.named_steps.keys())[-1]].feature_importances_
            else:
                logger.warning("Model does not have feature importances")
                return None
            
            if feature_names is None:
                feature_names = [f'Feature {i}' for i in range(len(importances))]
            
            # Get top N features
            indices = np.argsort(importances)[-top_n:]
            top_features = [feature_names[i] for i in indices]
            top_importances = importances[indices]
            
            fig, ax = plt.subplots(figsize=(12, 10))
            
            colors = plt.cm.viridis(np.linspace(0, 1, len(top_importances)))
            bars = ax.barh(range(len(top_importances)), top_importances, color=colors)
            ax.set_yticks(range(len(top_importances)))
            ax.set_yticklabels(top_features)
            ax.set_xlabel('Importance Score', fontsize=12)
            ax.set_ylabel('Feature', fontsize=12)
            ax.set_title(f'Top {top_n} Most Important Features', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for i, (bar, imp) in enumerate(zip(bars, top_importances)):
                ax.text(imp, i, f' {imp:.4f}', va='center', fontsize=9)
            
            plt.tight_layout()
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance plot saved to {save_path}")
            plt.close()
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error plotting feature importance: {e}")
            return None
    
    def plot_learning_curves(self, train_sizes: np.ndarray, train_scores: np.ndarray,
                            val_scores: np.ndarray, save_name: str = 'learning_curves.png'):
        """
        Plot learning curves
        
        Args:
            train_sizes: Training set sizes
            train_scores: Training scores
            val_scores: Validation scores
            save_name: Filename to save plot
        """
        logger.info("Creating learning curves...")
        
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        ax.plot(train_sizes, train_mean, 'o-', color='blue', label='Training Score')
        ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                        alpha=0.2, color='blue')
        
        ax.plot(train_sizes, val_mean, 'o-', color='red', label='Validation Score')
        ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std,
                        alpha=0.2, color='red')
        
        ax.set_xlabel('Training Set Size', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Learning Curves', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        save_path = os.path.join(self.output_dir, save_name)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Learning curves saved to {save_path}")
        plt.close()
        
        return save_path
    
    def create_comprehensive_report(self, y_true: np.ndarray, y_pred: np.ndarray,
                                   y_proba: np.ndarray, intent_mapping: dict,
                                   model_name: str = 'Model'):
        """
        Create comprehensive visualization report
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Prediction probabilities
            intent_mapping: Mapping from encoded labels to intent names
            model_name: Name of the model
        """
        logger.info(f"Creating comprehensive visualization report for {model_name}...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(self.output_dir, f"{model_name}_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        # Store original output dir
        original_output_dir = self.output_dir
        self.output_dir = report_dir
        
        paths = {}
        
        # Create all visualizations
        paths['confusion_matrix'] = self.plot_confusion_matrix(
            y_true, y_pred, intent_mapping, normalize=False
        )
        
        paths['confusion_matrix_normalized'] = self.plot_confusion_matrix(
            y_true, y_pred, intent_mapping, normalize=True, 
            save_name='confusion_matrix_normalized.png'
        )
        
        paths['classification_metrics'] = self.plot_classification_metrics(
            y_true, y_pred, y_proba, intent_mapping
        )
        
        # Restore original output dir
        self.output_dir = original_output_dir
        
        logger.info(f"Comprehensive report created in {report_dir}")
        return report_dir, paths


if __name__ == "__main__":
    # Test visualizer
    visualizer = IntentVisualizer()
    print("Visualizer initialized successfully!")

