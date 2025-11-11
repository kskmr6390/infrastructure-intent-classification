"""
Data Loader for Intent Classification System
Handles loading, parsing, and preprocessing of intent data
"""

import json
import re
import logging
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Handles data loading and preprocessing for intent classification"""
    
    def __init__(self, config: Dict):
        """
        Initialize DataLoader with configuration
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.label_encoder = LabelEncoder()
        self.intent_mapping = {}
        
    def parse_js_object_line(self, line: str) -> Dict:
        """
        Parse JavaScript-style object notation to Python dict
        Handles multiple formats
        
        Args:
            line: Line containing JS-style object
            
        Returns:
            Dictionary with parsed data
        """
        line = line.strip()
        if not line:
            return None
            
        # Try format 1: {query: 'text', intent: INTENT.name}
        query_match = re.search(r"query:\s*'([^']*)'", line)
        intent_match = re.search(r"intent:\s*INTENT\.(\w+)", line)
        
        if query_match and intent_match:
            return {
                'query': query_match.group(1),
                'intent': intent_match.group(1)
            }
        
        # Try format 2: {query: 'text', intent: Intent.name}
        query_match = re.search(r"query:\s*'([^']*)'", line)
        intent_match2 = re.search(r"intent:\s*Intent\.(\w+)", line)
        
        if query_match and intent_match2:
            return {
                'query': query_match.group(1),
                'intent': intent_match2.group(1)
            }
        
        # Try format 3: {query: 'text', intent: Intent. 'name} (with space)
        query_match = re.search(r"query:\s*'([^']*)'", line)
        intent_match3 = re.search(r"intent:\s*Intent\.\s*'?(\w+)", line)
        
        if query_match and intent_match3:
            return {
                'query': query_match.group(1),
                'intent': intent_match3.group(1)
            }
        
        return None
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from JSONL file
        
        Args:
            file_path: Path to data file
            
        Returns:
            DataFrame with queries and intents
        """
        logger.info(f"Loading data from {file_path}")
        
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                parsed = self.parse_js_object_line(line)
                if parsed:
                    data.append(parsed)
        
        df = pd.DataFrame(data)
        
        # Normalize intent names (handle both uppercase and lowercase)
        df['intent'] = df['intent'].str.lower()
        
        logger.info(f"Loaded {len(df)} samples with {df['intent'].nunique()} unique intents")
        logger.info(f"Intent distribution:\n{df['intent'].value_counts()}")
        
        return df
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text data
        
        Args:
            text: Input text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for training
        
        Args:
            df: DataFrame with queries and intents
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Preprocess queries
        df['processed_query'] = df['query'].apply(self.preprocess_text)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(df['intent'])
        
        # Create intent mapping for reference
        self.intent_mapping = dict(zip(
            self.label_encoder.transform(self.label_encoder.classes_),
            self.label_encoder.classes_
        ))
        
        logger.info(f"Intent mapping: {self.intent_mapping}")
        
        # Split data
        test_size = 1 - self.config['data']['train_test_split']
        random_seed = self.config['data']['random_seed']
        
        X_train, X_test, y_train, y_test = train_test_split(
            df['processed_query'].values,
            y_encoded,
            test_size=test_size,
            random_state=random_seed,
            stratify=y_encoded
        )
        
        logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        return X_train, X_test, y_train, y_test
    
    def get_label_encoder(self) -> LabelEncoder:
        """Return the label encoder"""
        return self.label_encoder
    
    def get_intent_mapping(self) -> Dict:
        """Return the intent mapping"""
        return self.intent_mapping
    
    def decode_intent(self, encoded_intent: int) -> str:
        """
        Decode encoded intent back to string
        
        Args:
            encoded_intent: Encoded intent label
            
        Returns:
            Intent string
        """
        return self.intent_mapping.get(encoded_intent, "unknown")


def load_config(config_path: str = 'config.yaml') -> Dict:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    import yaml
    import os
    
    # Support both old and new paths
    if not os.path.exists(config_path):
        # Try from project root
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', config_path)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


if __name__ == "__main__":
    # Test data loader
    config = load_config()
    loader = DataLoader(config)
    
    df = loader.load_data(config['data']['dataset_path'])
    X_train, X_test, y_train, y_test = loader.prepare_data(df)
    
    print(f"\nData loaded successfully!")
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    print(f"Number of intents: {len(loader.get_intent_mapping())}")

