# Usage Guide

Complete guide for using the Intent Classification System.

## System Overview

The Intent Classification System is a production-ready ML service that predicts user intents from infrastructure management queries. It features:

- Multiple ML models (Traditional ML + LLM)
- Modern web interface with chat-style UI
- Session management for organizing conversations
- Self-learning capabilities through feedback
- Real-time observability and monitoring

## Accessing the System

### Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

### API Documentation

Interactive API documentation is available at:
```
http://localhost:8000/docs
```

## Using the Web Interface

### 1. Creating a Chat Session

1. Open http://localhost:8000
2. Click "New Chat" to create a session
3. Optionally name your session for organization

### 2. Making Predictions

Enter your infrastructure-related query in the chat input:

**Example Queries:**
- "What is the CPU usage on server-01?"
- "Show network latency for router R1"
- "Check disk space on production servers"
- "Is the BGP session with ISP up?"
- "Find security alerts for IP 10.1.1.5"

The system will respond with:
- Predicted intent
- Confidence score
- Additional context

### 3. Understanding Confidence Scores

Confidence indicators help you trust predictions:

- **High (≥85%)**: Very confident, reliable prediction
- **Medium (70-85%)**: Moderately confident
- **Low (<70%)**: Uncertain, may need review

### 4. Providing Feedback

For incorrect predictions:
1. Click "Provide Feedback" button
2. Select or enter the correct intent
3. Submit feedback

The system stores feedback and improves over time through automatic retraining.

### 5. Managing Sessions

- **Switch Sessions**: Click on any session in the sidebar
- **Rename Session**: Use the session menu
- **Delete Session**: Remove unwanted sessions
- **View History**: All messages are saved per session

## Using the REST API

### Make a Prediction

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my-session",
    "message": "What is the network latency?"
  }'
```

### Python Example

```python
import requests

# Create a session
response = requests.post(
    "http://localhost:8000/api/sessions",
    json={"session_name": "Infrastructure Monitoring"}
)
session = response.json()
session_id = session['session']['session_id']

# Get prediction
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "session_id": session_id,
        "message": "Check CPU usage on web-server-01"
    }
)

result = response.json()
print(f"Intent: {result['prediction']['predicted_intent']}")
print(f"Confidence: {result['prediction']['confidence']:.1%}")
```

### Submit Feedback

```python
response = requests.post(
    "http://localhost:8000/api/feedback",
    json={
        "session_id": session_id,
        "message": "Show disk space",
        "predicted_intent": "wrong_intent",
        "correct_intent": "device_status_check",
        "confidence": 0.65
    }
)
```

## Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/docs` | GET | API documentation |
| `/api/health` | GET | System health check |
| `/api/chat` | POST | Get intent prediction |
| `/api/sessions` | GET | List all sessions |
| `/api/sessions` | POST | Create new session |
| `/api/sessions/{id}` | GET | Get session details |
| `/api/sessions/{id}` | PUT | Update session |
| `/api/sessions/{id}` | DELETE | Delete session |
| `/api/feedback` | POST | Submit feedback |
| `/api/observability/summary` | GET | System metrics |
| `/api/observability/predictions` | GET | Recent predictions |

## Training and Retraining Models

### Initial Training

```bash
# Interactive training script
./train_model.sh

# Or train specific models
source venv/bin/activate
python -m ml.traditional_ml.train
python -m ml.llm.train_llm
```

### Automatic Retraining

The system automatically retrains when:
- Sufficient feedback is collected (configurable threshold)
- Low-confidence predictions exceed threshold
- Scheduled retraining is triggered

Configure in `config.yaml`:
```yaml
self_learning:
  enabled: true
  min_samples_for_retrain: 10
  auto_retrain: true
```

### Manual Retraining

```bash
source venv/bin/activate
python -m ml.data.self_learning --retrain
```

## Self-Learning Features

### How It Works

1. **Prediction**: User asks a question, system predicts intent
2. **Uncertainty Detection**: Low confidence predictions are flagged
3. **Feedback Collection**: User corrections are stored
4. **Automatic Retraining**: Model improves when threshold is reached
5. **Continuous Improvement**: System gets better over time

### Viewing Feedback Statistics

```bash
source venv/bin/activate
python -m ml.data.self_learning --stats
```

### Exporting Feedback Data

Feedback is stored in:
- Database: `backend/database/chat_sessions.db`
- JSONL files: `ml/data/feedback/`

## Observability and Monitoring

### View System Metrics

```bash
# Command-line tool
python view_observability.py

# Or via API
curl http://localhost:8000/api/observability/summary
```

### LangSmith Integration (Optional)

For advanced observability, enable LangSmith in `config.yaml`:

```yaml
observability:
  enabled: true
  langsmith_enabled: true
  langsmith_project: "intent-classification"
```

Set environment variables:
```bash
export LANGSMITH_API_KEY="your-api-key"
export LANGCHAIN_TRACING_V2="true"
```

Restart the server to apply changes.

## Configuration

Edit `config.yaml` to customize:

### Model Selection

```yaml
model:
  type: "tfidf_svm"  # Options: tfidf_svm, llm, hybrid
```

### Training Parameters

```yaml
training:
  batch_size: 16
  test_size: 0.2
  random_state: 42
```

### Self-Learning Settings

```yaml
self_learning:
  enabled: true
  uncertainty_threshold: 0.7
  confidence_threshold: 0.85
  min_samples_for_retrain: 10
  auto_retrain: true
```

### Server Settings

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  log_level: "info"
```

## Visualizations

Training and evaluation generate visualizations in `visualizations/`:

- **Confusion Matrix**: Shows prediction accuracy per intent
- **Classification Metrics**: Precision, recall, F1-scores
- **Data Distribution**: Intent distribution in dataset
- **Training Split**: Train/test data split visualization

View these to understand model performance and identify areas for improvement.

## Troubleshooting

### Port Already in Use

```bash
# Use different port
PORT=8001 ./start.sh

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

### No Trained Models

```bash
# Train a model first
./train_model.sh
```

### Import Errors

```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors

```bash
# Check database file
ls -lh backend/database/chat_sessions.db

# View logs
tail -f server.log
```

### Low Confidence Predictions

1. Check if model is trained on relevant data
2. Add more training examples for that intent
3. Provide feedback to improve the model
4. Consider using LLM model for better semantic understanding

## Performance Optimization

### Choosing the Right Model

The system supports multiple models with different trade-offs:

- **TF-IDF + SVM**: Fast inference, low memory footprint, excellent for keyword-based queries
- **Sentence Transformers (LLM)**: Better semantic understanding, handles paraphrasing well
- **Hybrid**: Combines both approaches for balanced performance

Configure in `config.yaml`:
```yaml
model:
  type: "tfidf_svm"  # Options: tfidf_svm, llm, hybrid
```

See [ML Documentation](../ml/README.md) for implementation details.

### Caching

The system caches frequently used predictions. Clear cache to force fresh predictions:

```bash
# Restart server
./start.sh
```

## Best Practices

1. **Train with diverse data**: Include variations of queries
2. **Provide feedback**: Help the system learn from mistakes
3. **Monitor confidence**: Review low-confidence predictions
4. **Regular retraining**: Keep model up-to-date with feedback
5. **Use sessions**: Organize conversations for better tracking

## Next Steps

- [Setup Guide](SETUP_GUIDE.md) - Advanced configuration options
- [Quick Start](QUICK_START.md) - Quick reference guide
- [Backend Documentation](../backend/README.md) - API details
- [ML Documentation](../ml/README.md) - Model implementation details

## Support

- **Logs**: Check `server.log` for errors
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **GitHub Issues**: Report bugs and request features

---

**Happy classifying!**
