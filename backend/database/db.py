"""
Database module for session management
Uses SQLite to store chat sessions and messages
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatDatabase:
    """Handle database operations for chat sessions"""
    
    def __init__(self, db_path: str = 'chat_sessions.db'):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                session_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                predicted_intent TEXT,
                confidence REAL,
                top_predictions TEXT,
                is_uncertain BOOLEAN DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                query TEXT NOT NULL,
                predicted_intent TEXT NOT NULL,
                correct_intent TEXT NOT NULL,
                confidence REAL,
                is_correct BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages(message_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
            ON messages(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def create_session(self, session_name: str = None) -> str:
        """
        Create a new chat session
        
        Args:
            session_name: Name for the session
            
        Returns:
            Session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        if not session_name:
            session_name = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, session_name)
            VALUES (?, ?)
        ''', (session_id, session_name))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created session: {session_id} - {session_name}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session details
        
        Args:
            session_id: Session ID
            
        Returns:
            Session details or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Get all chat sessions
        
        Returns:
            List of sessions
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, COUNT(m.message_id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.session_id = m.session_id
            WHERE s.is_active = 1
            GROUP BY s.session_id
            ORDER BY s.updated_at DESC
        ''')
        
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return sessions
    
    def update_session_name(self, session_id: str, session_name: str):
        """
        Update session name
        
        Args:
            session_id: Session ID
            session_name: New session name
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET session_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_name, session_id))
        
        conn.commit()
        conn.close()
    
    def delete_session(self, session_id: str):
        """
        Soft delete a session
        
        Args:
            session_id: Session ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions 
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        logger.info(f"Deleted session: {session_id}")
    
    def add_message(self, session_id: str, role: str, content: str,
                   predicted_intent: str = None, confidence: float = None,
                   top_predictions: List[Dict] = None, is_uncertain: bool = False) -> int:
        """
        Add a message to a session
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant)
            content: Message content
            predicted_intent: Predicted intent
            confidence: Prediction confidence
            top_predictions: Top predictions list
            is_uncertain: Whether prediction is uncertain
            
        Returns:
            Message ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        top_predictions_json = json.dumps(top_predictions) if top_predictions else None
        
        cursor.execute('''
            INSERT INTO messages 
            (session_id, role, content, predicted_intent, confidence, 
             top_predictions, is_uncertain)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, role, content, predicted_intent, confidence,
              top_predictions_json, is_uncertain))
        
        message_id = cursor.lastrowid
        
        # Update session updated_at
        cursor.execute('''
            UPDATE sessions 
            SET updated_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """
        Get all messages for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of messages
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            message = dict(row)
            if message['top_predictions']:
                message['top_predictions'] = json.loads(message['top_predictions'])
            messages.append(message)
        
        conn.close()
        return messages
    
    def add_feedback(self, message_id: int, session_id: str, query: str,
                    predicted_intent: str, correct_intent: str,
                    confidence: float) -> int:
        """
        Add feedback for a prediction
        
        Args:
            message_id: Message ID
            session_id: Session ID
            query: Original query
            predicted_intent: Predicted intent
            correct_intent: Correct intent
            confidence: Prediction confidence
            
        Returns:
            Feedback ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        is_correct = (predicted_intent == correct_intent)
        
        cursor.execute('''
            INSERT INTO feedback 
            (message_id, session_id, query, predicted_intent, 
             correct_intent, confidence, is_correct)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, session_id, query, predicted_intent,
              correct_intent, confidence, is_correct))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Added feedback for message {message_id}")
        return feedback_id
    
    def get_session_statistics(self, session_id: str) -> Dict:
        """
        Get statistics for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Statistics dictionary
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Count messages
        cursor.execute('''
            SELECT COUNT(*) as total_messages,
                   COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
                   AVG(CASE WHEN confidence IS NOT NULL THEN confidence END) as avg_confidence
            FROM messages
            WHERE session_id = ?
        ''', (session_id,))
        
        stats = dict(cursor.fetchone())
        
        # Count uncertain predictions
        cursor.execute('''
            SELECT COUNT(*) as uncertain_count
            FROM messages
            WHERE session_id = ? AND is_uncertain = 1
        ''', (session_id,))
        
        stats['uncertain_predictions'] = cursor.fetchone()['uncertain_count']
        
        conn.close()
        return stats
    
    def get_all_feedback(self) -> List[Dict]:
        """
        Get all feedback
        
        Returns:
            List of feedback entries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM feedback
            ORDER BY timestamp DESC
        ''')
        
        feedback = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return feedback
    
    def export_feedback_to_jsonl(self, output_path: str):
        """
        Export feedback to JSONL format for retraining
        
        Args:
            output_path: Output file path
        """
        feedback = self.get_all_feedback()
        
        with open(output_path, 'w') as f:
            for entry in feedback:
                feedback_obj = {
                    'query': entry['query'],
                    'predicted_intent': entry['predicted_intent'],
                    'correct_intent': entry['correct_intent'],
                    'confidence': entry['confidence'],
                    'is_correct': entry['is_correct'],
                    'timestamp': entry['timestamp']
                }
                f.write(json.dumps(feedback_obj) + '\n')
        
        logger.info(f"Exported {len(feedback)} feedback entries to {output_path}")


if __name__ == "__main__":
    # Test database
    db = ChatDatabase()
    
    # Create test session
    session_id = db.create_session("Test Session")
    print(f"Created session: {session_id}")
    
    # Add messages
    db.add_message(session_id, "user", "Is the interface up?")
    db.add_message(session_id, "assistant", "Checking interface status...",
                  predicted_intent="network_status_check", confidence=0.95)
    
    # Get messages
    messages = db.get_session_messages(session_id)
    print(f"Messages: {len(messages)}")
    
    # Get all sessions
    sessions = db.get_all_sessions()
    print(f"Total sessions: {len(sessions)}")

