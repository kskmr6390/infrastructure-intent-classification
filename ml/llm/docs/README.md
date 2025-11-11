# LLM-based Intent Classification

Large Language Model (LLM) based intent classification using embeddings and fine-tuning.

## Available Models

### 1. Sentence Transformers (Recommended)
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Size**: 22M parameters
- **Best for**: Fast, accurate, low resource usage
- **Method**: Embedding similarity

### 2. TinyLlama
- **Model**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- **Size**: 1.1B parameters
- **Best for**: Chat-based classification
- **Method**: Prompt-based or fine-tuning

### 3. DistilBERT
- **Model**: `distilbert-base-uncased`
- **Size**: 66M parameters
- **Best for**: Classification tasks
- **Method**: Fine-tuning classifier head

## Configuration

In `config.yaml`:

```yaml
model:
  type: "llm"
  llm:
    model_name: "sentence-transformers/all-MiniLM-L6-v2"
    device: "cpu"  # or "cuda" for GPU
    temperature: 0.1
    max_length: 128
    batch_size: 16
```

## Training

### Embedding-based (Fast)
```bash
python -m ml.llm.train_llm
```

This method:
- Creates embeddings for each intent class
- Uses cosine similarity for classification
- No actual fine-tuning required
- Very fast training and inference

### Fine-tuning (Advanced)
```bash
python -m ml.llm.train_llm_custom
```

This method:
- Fine-tunes the model on your data
- Learns intent-specific patterns
- Better accuracy but slower
- Requires more GPU memory

## Inference

```python
from ml.llm.inference_llm import LLMIntentPredictor

predictor = LLMIntentPredictor()
result = predictor.predict("What is the network latency?")

print(f"Intent: {result['predicted_intent']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Hybrid Mode

Combine traditional ML with LLM:

```yaml
model:
  type: "hybrid"
  router:
    hybrid_mode: true
    confidence_threshold: 0.7
```

Benefits:
- Uses traditional model for high-confidence predictions (fast)
- Falls back to LLM for low-confidence cases (accurate)
- Best of both worlds

## Model Selection Guide

### Choose Sentence Transformers if:
- ✅ You want fast inference
- ✅ You have limited compute resources
- ✅ You need good accuracy with minimal setup

### Choose Fine-tuning if:
- ✅ You have GPU available
- ✅ You need maximum accuracy
- ✅ You have domain-specific terminology
- ✅ You can afford longer training time

### Choose Hybrid if:
- ✅ You want to balance speed and accuracy
- ✅ You have varying complexity queries
- ✅ You want robustness

## Performance Comparison

| Model | Accuracy | Speed | Memory | Training Time |
|-------|----------|-------|--------|---------------|
| TF-IDF+SVM | 85-90% | Very Fast | Low | 1-2 min |
| Sentence-T | 88-92% | Fast | Low | 5-10 min |
| Fine-tuned | 90-95% | Moderate | High | 30-60 min |
| Hybrid | 88-93% | Fast | Moderate | Varies |

## Temperature Setting

Controls confidence distribution:
- `temperature=0.1`: Sharp, confident predictions
- `temperature=0.5`: Balanced
- `temperature=1.0`: More uniform distribution

Lower temperature recommended for intent classification.

## Batch Processing

For bulk predictions:

```python
predictor = LLMIntentPredictor()
queries = ["query1", "query2", "query3"]

# Process in batches
for query in queries:
    result = predictor.predict(query)
    print(f"{query}: {result['predicted_intent']}")
```

## Troubleshooting

### Out of Memory
- Reduce `batch_size`
- Use smaller model
- Enable quantization
- Use CPU instead of GPU

### Slow Inference
- Use sentence-transformers
- Enable batching
- Use GPU if available

### Low Accuracy
- Try fine-tuning
- Increase training data
- Use hybrid mode
- Adjust temperature

