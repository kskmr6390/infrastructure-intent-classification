"""
Local Observability Module
Stores all predictions, feedback, and metrics locally without external dependencies
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class LocalObservabilityStore:
    """Local storage for predictions, feedback, and metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize local observability store
        
        Args:
            config: Observability configuration from config.yaml
        """
        self.config = config.get('local_observability', {})
        self.enabled = self.config.get('enabled', True)
        
        if not self.enabled:
            logger.info("Local observability disabled")
            return
        
        # Setup storage paths
        self.base_path = self.config.get('storage_path', 'observability_data')
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        
        # Database for structured queries
        self.db_path = os.path.join(self.base_path, 'observability.db')
        self._setup_database()
        
        # JSON files for backup/export
        self.predictions_file = os.path.join(self.base_path, 'predictions.jsonl')
        self.feedback_file = os.path.join(self.base_path, 'feedback.jsonl')
        self.metrics_file = os.path.join(self.base_path, 'metrics.json')
        
        # Thread lock for concurrent writes
        self._lock = threading.Lock()
        
        logger.info(f"✅ Local observability initialized at: {self.base_path}")
    
    def _setup_database(self):
        """Setup SQLite database for observability data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                predicted_intent TEXT NOT NULL,
                confidence REAL NOT NULL,
                is_out_of_scope BOOLEAN DEFAULT 0,
                is_uncertain BOOLEAN DEFAULT 0,
                predictor_type TEXT,
                model_type TEXT,
                session_id TEXT,
                top_predictions TEXT,
                metadata TEXT
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query TEXT NOT NULL,
                predicted_intent TEXT NOT NULL,
                correct_intent TEXT NOT NULL,
                confidence REAL NOT NULL,
                is_correct BOOLEAN,
                session_id TEXT,
                message_id INTEGER,
                metadata TEXT
            )
        ''')
        
        # Metrics table (aggregated stats)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_type TEXT,
                metadata TEXT
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pred_timestamp ON predictions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pred_intent ON predictions(predicted_intent)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pred_confidence ON predictions(confidence)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized at: {self.db_path}")
    
    def log_prediction(
        self,
        query: str,
        predicted_intent: str,
        confidence: float,
        all_predictions: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a prediction locally
        
        Args:
            query: Input query text
            predicted_intent: Predicted intent label
            confidence: Prediction confidence score
            all_predictions: List of all predictions with scores
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now().isoformat()
            
            # Prepare data
            is_out_of_scope = predicted_intent == 'out_of_scope'
            is_uncertain = metadata.get('is_uncertain', False) if metadata else False
            predictor_type = metadata.get('predictor_type', 'unknown') if metadata else 'unknown'
            model_type = metadata.get('model_type', 'unknown') if metadata else 'unknown'
            session_id = metadata.get('session_id', '') if metadata else ''
            
            # Store in database
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO predictions (
                        timestamp, query, predicted_intent, confidence,
                        is_out_of_scope, is_uncertain, predictor_type, model_type,
                        session_id, top_predictions, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    query,
                    predicted_intent,
                    confidence,
                    is_out_of_scope,
                    is_uncertain,
                    predictor_type,
                    model_type,
                    session_id,
                    json.dumps(all_predictions) if all_predictions else None,
                    json.dumps(metadata) if metadata else None
                ))
                
                conn.commit()
                conn.close()
            
            # Append to JSONL file for easy export
            prediction_data = {
                'timestamp': timestamp,
                'query': query,
                'predicted_intent': predicted_intent,
                'confidence': confidence,
                'is_out_of_scope': is_out_of_scope,
                'is_uncertain': is_uncertain,
                'predictor_type': predictor_type,
                'model_type': model_type,
                'all_predictions': all_predictions,
                'metadata': metadata
            }
            
            with self._lock:
                with open(self.predictions_file, 'a') as f:
                    f.write(json.dumps(prediction_data) + '\n')
            
            logger.debug(f"Logged prediction: {predicted_intent} ({confidence:.2%})")
            
        except Exception as e:
            logger.error(f"Failed to log prediction locally: {e}")
    
    def log_feedback(
        self,
        query: str,
        predicted_intent: str,
        correct_intent: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log user feedback locally
        
        Args:
            query: Input query text
            predicted_intent: Predicted intent
            correct_intent: Correct intent (from user feedback)
            confidence: Prediction confidence
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now().isoformat()
            is_correct = predicted_intent == correct_intent
            session_id = metadata.get('session_id', '') if metadata else ''
            message_id = metadata.get('message_id', 0) if metadata else 0
            
            # Store in database
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO feedback (
                        timestamp, query, predicted_intent, correct_intent,
                        confidence, is_correct, session_id, message_id, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    query,
                    predicted_intent,
                    correct_intent,
                    confidence,
                    is_correct,
                    session_id,
                    message_id,
                    json.dumps(metadata) if metadata else None
                ))
                
                conn.commit()
                conn.close()
            
            # Append to JSONL file
            feedback_data = {
                'timestamp': timestamp,
                'query': query,
                'predicted_intent': predicted_intent,
                'correct_intent': correct_intent,
                'confidence': confidence,
                'is_correct': is_correct,
                'metadata': metadata
            }
            
            with self._lock:
                with open(self.feedback_file, 'a') as f:
                    f.write(json.dumps(feedback_data) + '\n')
            
            logger.info(f"Logged feedback: {predicted_intent} -> {correct_intent}")
            
        except Exception as e:
            logger.error(f"Failed to log feedback locally: {e}")
    
    def log_metric(self, metric_name: str, metric_value: float, metric_type: str = 'gauge', metadata: Optional[Dict] = None):
        """Log a custom metric"""
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now().isoformat()
            
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO metrics (timestamp, metric_name, metric_value, metric_type, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    metric_name,
                    metric_value,
                    metric_type,
                    json.dumps(metadata) if metadata else None
                ))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.error(f"Failed to log metric: {e}")
    
    def get_statistics(self, time_range: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive statistics
        
        Args:
            time_range: Time range filter (e.g., '24h', '7d', '30d')
        
        Returns:
            Statistics dictionary
        """
        if not self.enabled:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Calculate time filter
            time_filter = ""
            if time_range:
                from datetime import timedelta
                hours = {'24h': 24, '7d': 168, '30d': 720}.get(time_range, 24)
                cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
                time_filter = f"WHERE timestamp > '{cutoff}'"
            
            # Total predictions
            cursor.execute(f'SELECT COUNT(*) as count FROM predictions {time_filter}')
            total_predictions = cursor.fetchone()['count']
            
            # Average confidence
            cursor.execute(f'SELECT AVG(confidence) as avg_conf FROM predictions {time_filter}')
            avg_confidence = cursor.fetchone()['avg_conf'] or 0
            
            # Out of scope count
            cursor.execute(f'SELECT COUNT(*) as count FROM predictions {time_filter} AND is_out_of_scope = 1')
            out_of_scope_count = cursor.fetchone()['count']
            
            # Uncertain predictions
            cursor.execute(f'SELECT COUNT(*) as count FROM predictions {time_filter} AND is_uncertain = 1')
            uncertain_count = cursor.fetchone()['count']
            
            # Total feedback
            cursor.execute(f'SELECT COUNT(*) as count FROM feedback {time_filter}')
            total_feedback = cursor.fetchone()['count']
            
            # Accuracy from feedback
            cursor.execute(f'SELECT AVG(CAST(is_correct AS FLOAT)) as accuracy FROM feedback {time_filter}')
            feedback_accuracy = cursor.fetchone()['accuracy'] or 0
            
            # Top predicted intents
            cursor.execute(f'''
                SELECT predicted_intent, COUNT(*) as count 
                FROM predictions {time_filter} AND is_out_of_scope = 0
                GROUP BY predicted_intent 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            top_intents = [dict(row) for row in cursor.fetchall()]
            
            # Confidence distribution
            cursor.execute(f'''
                SELECT 
                    SUM(CASE WHEN confidence >= 0.9 THEN 1 ELSE 0 END) as very_high,
                    SUM(CASE WHEN confidence >= 0.7 AND confidence < 0.9 THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN confidence >= 0.5 AND confidence < 0.7 THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN confidence < 0.5 THEN 1 ELSE 0 END) as low
                FROM predictions {time_filter}
            ''')
            conf_dist = dict(cursor.fetchone())
            
            conn.close()
            
            return {
                'total_predictions': total_predictions,
                'average_confidence': round(avg_confidence, 4),
                'out_of_scope_count': out_of_scope_count,
                'out_of_scope_rate': round(out_of_scope_count / max(total_predictions, 1), 4),
                'uncertain_count': uncertain_count,
                'uncertain_rate': round(uncertain_count / max(total_predictions, 1), 4),
                'total_feedback': total_feedback,
                'feedback_accuracy': round(feedback_accuracy, 4),
                'top_intents': top_intents,
                'confidence_distribution': conf_dist,
                'time_range': time_range or 'all_time'
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def get_recent_predictions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent predictions"""
        if not self.enabled:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM predictions 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get recent predictions: {e}")
            return []
    
    def get_intent_performance(self) -> Dict[str, Any]:
        """Get per-intent performance statistics"""
        if not self.enabled:
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get prediction counts and avg confidence per intent
            cursor.execute('''
                SELECT 
                    predicted_intent,
                    COUNT(*) as prediction_count,
                    AVG(confidence) as avg_confidence,
                    MIN(confidence) as min_confidence,
                    MAX(confidence) as max_confidence,
                    SUM(CASE WHEN is_uncertain = 1 THEN 1 ELSE 0 END) as uncertain_count
                FROM predictions
                WHERE is_out_of_scope = 0
                GROUP BY predicted_intent
                ORDER BY prediction_count DESC
            ''')
            
            intent_stats = {}
            for row in cursor.fetchall():
                intent = row['predicted_intent']
                intent_stats[intent] = {
                    'prediction_count': row['prediction_count'],
                    'avg_confidence': round(row['avg_confidence'], 4),
                    'min_confidence': round(row['min_confidence'], 4),
                    'max_confidence': round(row['max_confidence'], 4),
                    'uncertain_count': row['uncertain_count'],
                    'uncertain_rate': round(row['uncertain_count'] / row['prediction_count'], 4)
                }
            
            # Add feedback accuracy per intent
            cursor.execute('''
                SELECT 
                    predicted_intent,
                    COUNT(*) as feedback_count,
                    AVG(CAST(is_correct AS FLOAT)) as accuracy
                FROM feedback
                GROUP BY predicted_intent
            ''')
            
            for row in cursor.fetchall():
                intent = row['predicted_intent']
                if intent in intent_stats:
                    intent_stats[intent]['feedback_count'] = row['feedback_count']
                    intent_stats[intent]['feedback_accuracy'] = round(row['accuracy'], 4)
            
            conn.close()
            
            return intent_stats
            
        except Exception as e:
            logger.error(f"Failed to get intent performance: {e}")
            return {}
    
    def export_data(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Export all data to JSON files
        
        Args:
            output_dir: Output directory (defaults to base_path/exports)
        
        Returns:
            Dictionary with paths to exported files
        """
        if not self.enabled:
            return {}
        
        try:
            export_dir = output_dir or os.path.join(self.base_path, 'exports')
            Path(export_dir).mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            exported_files = {}
            
            # Export predictions
            cursor.execute('SELECT * FROM predictions ORDER BY timestamp')
            predictions = [dict(row) for row in cursor.fetchall()]
            pred_file = os.path.join(export_dir, f'predictions_{timestamp}.json')
            with open(pred_file, 'w') as f:
                json.dump(predictions, f, indent=2)
            exported_files['predictions'] = pred_file
            
            # Export feedback
            cursor.execute('SELECT * FROM feedback ORDER BY timestamp')
            feedback = [dict(row) for row in cursor.fetchall()]
            feedback_file = os.path.join(export_dir, f'feedback_{timestamp}.json')
            with open(feedback_file, 'w') as f:
                json.dump(feedback, f, indent=2)
            exported_files['feedback'] = feedback_file
            
            # Export statistics
            stats = self.get_statistics()
            stats_file = os.path.join(export_dir, f'statistics_{timestamp}.json')
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            exported_files['statistics'] = stats_file
            
            # Export intent performance
            intent_perf = self.get_intent_performance()
            perf_file = os.path.join(export_dir, f'intent_performance_{timestamp}.json')
            with open(perf_file, 'w') as f:
                json.dump(intent_perf, f, indent=2)
            exported_files['intent_performance'] = perf_file
            
            conn.close()
            
            logger.info(f"Data exported to: {export_dir}")
            return exported_files
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return {}
    
    def clear_old_data(self, days: int = 30):
        """
        Clear data older than specified days
        
        Args:
            days: Number of days to keep
        """
        if not self.enabled:
            return
        
        try:
            from datetime import timedelta
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM predictions WHERE timestamp < ?', (cutoff,))
                pred_deleted = cursor.rowcount
                
                cursor.execute('DELETE FROM feedback WHERE timestamp < ?', (cutoff,))
                feedback_deleted = cursor.rowcount
                
                cursor.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff,))
                metrics_deleted = cursor.rowcount
                
                conn.commit()
                conn.close()
            
            logger.info(f"Cleaned old data: {pred_deleted} predictions, {feedback_deleted} feedback, {metrics_deleted} metrics")
            
        except Exception as e:
            logger.error(f"Failed to clear old data: {e}")


# Singleton instance
_local_observability_store: Optional[LocalObservabilityStore] = None


def get_local_observability_store(config: Optional[Dict[str, Any]] = None) -> LocalObservabilityStore:
    """
    Get or create local observability store singleton
    
    Args:
        config: Observability configuration (only used on first call)
    
    Returns:
        LocalObservabilityStore instance
    """
    global _local_observability_store
    
    if _local_observability_store is None:
        if config is None:
            config = {'local_observability': {'enabled': True}}
        _local_observability_store = LocalObservabilityStore(config)
    
    return _local_observability_store

