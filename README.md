# Intent Classification System

A production-ready machine learning system for classifying user intents in infrastructure management queries using FastAPI backend and multiple ML models.

## Quick Start

```bash
# 1. Make scripts executable
chmod +x *.sh

# 2. Train a model
./train_model.sh

# 3. Start server
./start.sh
```

**Web Interface:** http://localhost:8000  
**API Documentation:** http://localhost:8000/docs

## Project Structure

```
intent_classification/
├── backend/            # FastAPI REST API
│   ├── api/           # API endpoints
│   ├── core/          # Core services
│   └── database/      # Database layer
├── frontend/          # Web interface
├── ml/                # Machine learning
│   ├── data/         # Data handling
│   ├── llm/          # LLM models
│   ├── traditional_ml/ # SVM, RF models
│   └── model/        # Saved models
├── guides/           # Documentation
└── config.yaml       # Configuration
```

## Features

- **Multiple ML Models**: Traditional (SVM, Random Forest) and LLM-based classifiers
- **FastAPI Backend**: Modern async API with automatic documentation
- **Self-Learning**: Continuous improvement from user feedback
- **LangSmith Integration**: Real-time observability and monitoring
- **Docker Support**: Containerized deployment
- **Session Management**: Multi-session chat support

## Training Models

```bash
# Interactive training script
./train_model.sh

# Or train specific models directly
python -m ml.traditional_ml.train  # Traditional ML (1-2 min)
python -m ml.llm.train_llm         # LLM model (5-10 min)
```

## Running the System

### Local Development

```bash
# Production mode
./start.sh

# Development mode (auto-reload)
./start_dev.sh
```

### Docker Deployment

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration

Edit `config.yaml` to configure the system:

```yaml
model:
  type: "tfidf_svm"  # Options: tfidf_svm, llm, hybrid
  
data:
  dataset_path: "ml/data/raw/infra_copilot_intent_dataset_v2.jsonl"
  
observability:
  enabled: true
  langsmith_enabled: false
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/docs` | GET | API documentation (Swagger) |
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Intent prediction |
| `/api/sessions` | GET/POST/PUT/DELETE | Session management |
| `/api/feedback` | POST | Submit feedback |
| `/api/observability/*` | GET | Observability data |

## Testing the API

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Prediction
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "message": "What is the CPU usage?"
  }'
```

### Python Client
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"session_id": "test", "message": "Show network latency"}
)

result = response.json()
print(f"Intent: {result['prediction']['predicted_intent']}")
print(f"Confidence: {result['prediction']['confidence']:.2%}")
```

## Model Performance

| Model | Accuracy | Speed | Memory | Training Time |
|-------|----------|-------|--------|---------------|
| TF-IDF + SVM | 85-90% | Fast | Low | 1-2 min |
| Sentence Transformer | 88-92% | Medium | Low | 5-10 min |
| Fine-tuned LLM | 90-95% | Slow | High | 30-60 min |
| Hybrid | 88-93% | Medium | Medium | Varies |

## Documentation

### User Guides

| Guide | Description |
|-------|-------------|
| [Quick Start](guides/QUICK_START.md) | Get running in 5 minutes |
| [Setup Guide](guides/SETUP_GUIDE.md) | Detailed installation instructions |
| [Usage Guide](guides/USAGE_GUIDE.md) | How to use the system |

### Component Documentation

- **Backend API**: [backend/README.md](backend/README.md)
- **Frontend**: [frontend/README.md](frontend/README.md)
- **ML Models**: [ml/README.md](ml/README.md)
- **Traditional ML**: [ml/traditional_ml/docs/](ml/traditional_ml/docs/)
- **LLM Models**: [ml/llm/docs/](ml/llm/docs/)
- **Data Handling**: [ml/data/docs/](ml/data/docs/)

## Requirements

- Python 3.9+
- 2GB RAM minimum (4GB recommended)
- 1GB disk space
- Docker (optional, for containerized deployment)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | `PORT=8001 ./start.sh` |
| Import errors | `source venv/bin/activate` |
| No trained models | Run `./train_model.sh` |
| Out of memory | Reduce `batch_size` in config.yaml |
| Module not found | `pip install -r requirements.txt` |

See the [Setup Guide](guides/SETUP_GUIDE.md) for detailed troubleshooting.

## Self-Learning System

The system improves continuously through user feedback:

1. User provides feedback on predictions
2. Feedback is collected in `ml/data/feedback/`
3. System retrains when feedback threshold is reached
4. Improved model is automatically deployed

## Observability

View prediction metrics and feedback:

```bash
# View observability dashboard
python view_observability.py

# Access via API
curl http://localhost:8000/api/observability/summary
```

## License

[Your License Here]

---

**Tech Stack:** FastAPI | PyTorch | Scikit-learn | Transformers

**Ready to start?** Run `./train_model.sh` then `./start.sh`
