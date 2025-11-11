# Model Documentation

## Saved Models

This directory contains trained models ready for inference.

## Model Files

### Traditional ML Models
- `tfidf_svm_model_{timestamp}.pkl` - TF-IDF + SVM model
- `label_encoder_{timestamp}.pkl` - Label encoder
- `intent_mapping_{timestamp}.pkl` - Intent mapping

### LLM Models
- `llm_model_{timestamp}.pkl` - LLM embeddings and metadata
- `llm_metadata_{timestamp}.pkl` - Model metadata
- `llm_intent_mapping_{timestamp}.pkl` - Intent mapping
- `llm_label_encoder_{timestamp}.pkl` - Label encoder

## Model Selection

The system automatically loads the most recent model based on timestamp.

## Model Versioning

Models are versioned using timestamps in format: `YYYYMMDD_HHMMSS`

Example: `tfidf_svm_model_20251112_015713.pkl`

## Model Performance

Each model includes:
- Training accuracy
- Test accuracy
- Confusion matrix
- Per-class metrics
- Visualization plots

## Loading Models

### For Inference
Models are automatically loaded by the predictor:

```python
from ml.traditional_ml.inference import IntentPredictor
predictor = IntentPredictor()
result = predictor.predict("Your query here")
```

### Manual Loading
```python
import joblib
model = joblib.load('ml/model/saved_models/tfidf_svm_model_{timestamp}.pkl')
```

## Model Retraining

Models should be retrained when:
- New training data is available
- Feedback threshold is reached
- Performance degrades
- Intent categories change

## Best Practices

1. Keep at least 2-3 recent models as backup
2. Test new models before deployment
3. Document model changes
4. Monitor model performance
5. Version control configuration files

