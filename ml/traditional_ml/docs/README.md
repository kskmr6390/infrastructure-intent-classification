# Traditional ML Models

Traditional machine learning models for intent classification.

## Available Models

### 1. TF-IDF + SVM (Support Vector Machine)
- **Best for**: High accuracy, interpretable results
- **Training time**: Fast
- **Inference time**: Very fast
- **Memory**: Low

Configuration in `config.yaml`:
```yaml
model:
  type: "tfidf_svm"
  tfidf:
    max_features: 5000
    ngram_range: [1, 3]
  svm:
    kernel: "linear"
    C: 10.0
    probability: true
```

### 2. TF-IDF + Random Forest
- **Best for**: Robust to overfitting, handles imbalanced data
- **Training time**: Moderate
- **Inference time**: Fast
- **Memory**: Moderate

Configuration:
```yaml
model:
  type: "tfidf_rf"
  random_forest:
    n_estimators: 200
    max_depth: 50
```

### 3. Ensemble Models
- Combines multiple models for better accuracy
- Voting or stacking strategies

## Training

```bash
# Train TF-IDF + SVM
python -m ml.traditional_ml.train --config config.yaml

# Train with specific dataset
python -m ml.traditional_ml.train --config config.yaml --data ml/data/raw/dataset.jsonl
```

## Evaluation

```bash
python -m ml.traditional_ml.evaluate
```

Outputs:
- Accuracy metrics
- Confusion matrix
- Per-class precision/recall/F1
- Visualizations in `visualizations/` directory

## Inference

```python
from ml.traditional_ml.inference import IntentPredictor

predictor = IntentPredictor()
result = predictor.predict("What is the CPU usage?")

print(f"Intent: {result['predicted_intent']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Visualization

The `visualizer.py` module creates:
- Data distribution plots
- Confusion matrices
- Training/test split visualization
- Per-class metrics

## Model Components

### TF-IDF Vectorizer
- Converts text to numerical features
- Captures word importance
- Handles n-grams

### SVM Classifier
- Linear kernel for text classification
- Probability calibration
- Class weight balancing

### Random Forest
- Ensemble of decision trees
- Feature importance ranking
- Robust to noise

## Hyperparameter Tuning

Key parameters to tune:
1. TF-IDF `max_features`: 1000-10000
2. TF-IDF `ngram_range`: [1,2] or [1,3]
3. SVM `C`: 1.0, 10.0, 100.0
4. RF `n_estimators`: 100-500
5. RF `max_depth`: 20-100

## Performance Tips

1. Use calibration for better confidence scores
2. Balance class weights for imbalanced data
3. Use cross-validation for robust evaluation
4. Monitor uncertain predictions
5. Retrain periodically with new data

