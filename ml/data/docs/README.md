# Data Documentation

## Dataset Structure

### Raw Data Format

Intent classification data is stored in JSONL format:

```javascript
{query: 'What is the current network latency?', intent: INTENT.NETWORK_LATENCY}
{query: 'Show me CPU usage', intent: INTENT.RESOURCE_MONITORING}
```

### Intent Categories

The system classifies queries into predefined intent categories related to infrastructure management.

## Data Files

### Raw Datasets
- `infra_copilot_intent_dataset_v1_1.jsonl` - Version 1.1 dataset
- `infra_copilot_intent_dataset_v2.jsonl` - Version 2 dataset
- `infra_copilot_intent_dataset_v3.jsonl` - Version 3 dataset

### Feedback Data
- `feedback.jsonl` - User feedback on predictions
- `uncertain_predictions.jsonl` - Low confidence predictions

## Data Loader

The `data_loader.py` module provides:
- JSONL parsing
- Text preprocessing
- Train/test splitting
- Label encoding

## Self-Learning System

The `self_learning.py` module handles:
- Collecting user feedback
- Identifying uncertain predictions
- Preparing data for retraining
- Active learning strategies

## Data Statistics

Run the following to see data statistics:

```python
from ml.data.data_loader import DataLoader, load_config

config = load_config('config.yaml')
loader = DataLoader(config)
df = loader.load_data('ml/data/raw/infra_copilot_intent_dataset_v2.jsonl')
print(df['intent'].value_counts())
```

## Data Quality

- Minimum samples per intent: Configured in `config.yaml`
- Train/test split: 80/20 (configurable)
- Stratified sampling: Yes
- Data validation: Automated checks during loading

