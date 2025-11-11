# Intent Classification System

> **🚀 Production-Ready ML System with FastAPI Backend**

A modern machine learning system for classifying user intents in infrastructure management queries.

## 📁 Project Structure

```
intent_classification/
├── frontend/           # 🎨 Web Interface
├── backend/            # 🚀 FastAPI REST API
├── ml/                 # 🤖 Machine Learning
│   ├── data/          # Data handling
│   ├── model/         # Saved models
│   ├── traditional_ml/  # SVM, RF models
│   └── llm/           # LLM models
├── guides/            # 📚 Documentation
└── config.yaml        # ⚙️ Configuration
```

## 🚀 Quick Start

```bash
# 1. Make scripts executable
chmod +x *.sh

# 2. Train a model
./train_model.sh

# 3. Start server
./start.sh
```

**Access at:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

## ✨ Features

- ✅ **Multiple ML Models**: Traditional (SVM, RF) + LLM-based
- ✅ **FastAPI Backend**: Modern, async, auto-documented API
- ✅ **Self-Learning**: Improves from user feedback
- ✅ **LangSmith Observability**: Track predictions and feedback in real-time
- ✅ **Docker Ready**: Containerized deployment
- ✅ **Production Ready**: Logging, monitoring, error handling

## 📚 Documentation

### Essential Guides

| Guide | Description | When to Use |
|-------|-------------|-------------|
| [**Quick Start**](guides/QUICK_START.md) | Get running in 5 minutes | ⚡ First time setup |
| [**Setup Guide**](guides/SETUP_GUIDE.md) | Detailed installation | 📦 Complete installation |
| [**Usage Guide**](guides/USAGE_GUIDE.md) | How to use the system | 💡 Daily usage |
| [**Migration Guide**](guides/MIGRATION_GUIDE.md) | Flask to FastAPI upgrade | 🔄 Upgrading |
| [**Model Selector**](guides/MODEL_SELECTOR_GUIDE.md) | Choose the right model | 🎯 Model selection |
| [**LLM Setup**](guides/LLM_SETUP.md) | LLM configuration | 🤖 Advanced models |
| [**LangSmith Observability**](guides/LANGSMITH_OBSERVABILITY.md) | Monitor & debug predictions | 🔍 Observability |

**📖 View all guides:**
- **Markdown:** See [`guides/`](guides/) folder
- **Web UI:** http://localhost:8000/guides/ (when server running)
- **Index Page:** http://localhost:8000/guides/index.html

### Component Documentation

- **Frontend**: [`frontend/README.md`](frontend/README.md) - Web interface
- **Backend**: [`backend/README.md`](backend/README.md) - API documentation
- **ML**: [`ml/README.md`](ml/README.md) - Machine learning
- **Data**: [`ml/data/docs/`](ml/data/docs/) - Data handling
- **Traditional ML**: [`ml/traditional_ml/docs/`](ml/traditional_ml/docs/) - SVM, RF models
- **LLM**: [`ml/llm/docs/`](ml/llm/docs/) - LLM models

## 🎯 Training Models

```bash
# Interactive training script
./train_model.sh

# Or train specific models
python -m ml.traditional_ml.train  # Fast (1-2 min)
python -m ml.llm.train_llm         # Accurate (5-10 min)
```

## 🖥️ Running the System

### Local Development

```bash
# Production mode
./start.sh

# Development mode (auto-reload)
./start_dev.sh

# Or with uvicorn directly
uvicorn backend.main:app --reload
```

### Docker Deployment

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🔧 Configuration

**Main Config:** [`config.yaml`](config.yaml)
```yaml
model:
  type: "tfidf_svm"  # Options: tfidf_svm, llm, hybrid
data:
  dataset_path: "ml/data/raw/infra_copilot_intent_dataset_v2.jsonl"
```

**Environment:** `.env` (optional)
```bash
DEBUG=true
PORT=8000
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/docs` | GET | API documentation (Swagger) |
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Intent prediction |
| `/api/sessions` | GET/POST/PUT/DELETE | Session management |
| `/api/feedback` | POST | Submit feedback |

## 🧪 Testing

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

## 📈 Model Performance

| Model | Accuracy | Speed | Memory | Training Time |
|-------|----------|-------|--------|---------------|
| TF-IDF + SVM | 85-90% | ⚡⚡⚡ | Low | 1-2 min |
| Sentence-T | 88-92% | ⚡⚡ | Low | 5-10 min |
| Fine-tuned LLM | 90-95% | ⚡ | High | 30-60 min |
| Hybrid | 88-93% | ⚡⚡ | Medium | Varies |

## 🔄 Self-Learning

The system continuously improves through user feedback:

1. User corrects predictions
2. System collects feedback
3. Retrains when threshold reached
4. Deploys improved model

Feedback stored in: `ml/data/feedback/`

## 📦 Requirements

- **Python**: 3.9 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 1GB free space
- **Optional**: Docker for containerized deployment

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | `PORT=8001 ./start.sh` |
| Import errors | `source venv/bin/activate` |
| No trained models | Run `./train_model.sh` |
| Out of memory | Reduce `batch_size` in config.yaml |
| Module not found | `pip install -r requirements.txt` |

See [**Setup Guide**](guides/SETUP_GUIDE.md) for detailed troubleshooting.

## 📖 Learning Path

1. **New User?** → [Quick Start Guide](guides/QUICK_START.md) ⚡
2. **Need Setup Details?** → [Setup Guide](guides/SETUP_GUIDE.md) 📦
3. **Want to Use It?** → [Usage Guide](guides/USAGE_GUIDE.md) 💡
4. **Choosing Model?** → [Model Selector](guides/MODEL_SELECTOR_GUIDE.md) 🎯
5. **Upgrading?** → [Migration Guide](guides/MIGRATION_GUIDE.md) 🔄
6. **API Details?** → Visit http://localhost:8000/docs 📚

## 🎓 Example Usage

### Web Interface
1. Open http://localhost:8000
2. Create a new session
3. Type your query
4. Get intent prediction with confidence
5. Provide feedback to improve

### REST API
```python
import requests

# Create session
session = requests.post(
    "http://localhost:8000/api/sessions",
    json={"session_name": "My Session"}
).json()

session_id = session['session']['session_id']

# Get prediction
prediction = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "session_id": session_id,
        "message": "Check server health status"
    }
).json()

print(f"Intent: {prediction['prediction']['predicted_intent']}")
print(f"Confidence: {prediction['prediction']['confidence']:.2%}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Support

- **Documentation**: [`guides/`](guides/) folder
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: GitHub Issues
- **Component Docs**: Check README files in subdirectories

## 🔗 Quick Links

- 📚 [All Guides](guides/)
- 🎨 [Frontend Docs](frontend/README.md)
- 🚀 [Backend Docs](backend/README.md)
- 🤖 [ML Docs](ml/README.md)
- 📊 [API Reference](http://localhost:8000/docs)

---

**Made with** FastAPI ⚡ | PyTorch 🔥 | Scikit-learn 🧠

**Ready to start?** Run `./train_model.sh` then `./start.sh` 🚀
