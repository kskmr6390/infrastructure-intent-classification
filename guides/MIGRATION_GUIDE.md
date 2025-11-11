# Migration Guide: Flask to FastAPI

This document explains the changes from the old structure to the new structure.

## Old vs New Structure

### Old Structure (Flask)
```
intent_classification/
├── web_app.py              # Flask application
├── data_loader.py          # Data loading
├── model.py                # ML models
├── llm_model.py            # LLM models
├── train.py                # Training
├── inference.py            # Inference
├── templates/              # HTML templates
├── static/                 # Static files
└── models/                 # Saved models
```

### New Structure (FastAPI)
```
intent_classification/
├── frontend/               # Web interface
│   ├── static/
│   └── templates/
├── backend/                # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Core modules
│   └── database/          # Database
├── ml/                     # Machine learning
│   ├── data/              # Data handling
│   ├── model/             # Model storage
│   ├── traditional_ml/    # Traditional ML
│   └── llm/               # LLM models
└── config.yaml            # Configuration
```

## Key Changes

### 1. Web Framework: Flask → FastAPI

**Old (Flask):**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    return jsonify(result)
```

**New (FastAPI):**
```python
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(request: ChatRequest):
    return result
```

### 2. Import Paths

**Old imports:**
```python
from data_loader import DataLoader
from model import create_classifier
from inference import IntentPredictor
from llm_model import LLMIntentClassifier
```

**New imports:**
```python
from ml.data.data_loader import DataLoader
from ml.traditional_ml.model import create_classifier
from ml.traditional_ml.inference import IntentPredictor
from ml.llm.llm_model import LLMIntentClassifier
```

### 3. Configuration Paths

Update paths in `config.yaml`:
- `dataset_path`: `"infra_copilot_intent_dataset_v2.jsonl"` → `"ml/data/raw/infra_copilot_intent_dataset_v2.jsonl"`
- `model_save_path`: `"models/"` → `"ml/model/saved_models/"`
- `feedback_storage_path`: `"feedback_data/"` → `"ml/data/feedback/"`

### 4. Running the Application

**Old:**
```bash
python web_app.py
```

**New:**
```bash
# Using startup script
./start.sh

# Or directly
python -m backend.main

# Or with uvicorn
uvicorn backend.main:app --reload
```

### 5. Training Models

**Old:**
```bash
python train.py
python train_llm.py
```

**New:**
```bash
# Using script
./train_model.sh

# Or directly
python -m ml.traditional_ml.train
python -m ml.llm.train_llm
```

### 6. API Endpoints

The endpoints remain the same, but now served by FastAPI:

- `POST /api/chat` - Chat with intent prediction
- `GET /api/sessions` - Get sessions
- `POST /api/feedback` - Submit feedback
- `GET /api/health` - Health check

**New Feature:** Automatic API documentation at `/docs`

### 7. Configuration

**Old:** Hardcoded or in `config.yaml`

**New:** 
- `config.yaml` - ML configuration
- `.env` - Environment variables
- `backend/core/config.py` - Application settings

### 8. Database Path

**Old:**
```python
db = ChatDatabase()  # Uses default path
```

**New:**
```python
from backend.core.config import get_settings
settings = get_settings()
db = ChatDatabase(settings.DATABASE_PATH)
```

## Benefits of New Structure

### 1. Better Organization
- Clear separation: Frontend, Backend, ML
- Each component has its own docs
- Easier to navigate and maintain

### 2. Scalability
- Can deploy backend separately from ML
- Can scale components independently
- Better for microservices architecture

### 3. Development Experience
- FastAPI auto-generates API docs
- Type hints for better IDE support
- Async/await for better performance
- Pydantic validation

### 4. Testing
- Easier to test individual components
- Mock dependencies more easily
- Separate unit tests by module

### 5. Deployment
- Docker support out of the box
- Environment-based configuration
- Production-ready setup

## Migration Steps

If you have an existing deployment:

1. **Backup your data:**
   ```bash
   cp -r models/ ml/model/saved_models/
   cp -r feedback_data/ ml/data/feedback/
   cp chat_sessions.db backend/database/
   ```

2. **Install new dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Update any custom scripts:**
   - Change import paths
   - Update file paths in config
   - Use new startup scripts

4. **Test the system:**
   ```bash
   # Train a model
   ./train_model.sh
   
   # Start the server
   ./start.sh
   
   # Test at http://localhost:8000
   ```

5. **Update deployment:**
   - Use new Docker setup
   - Update environment variables
   - Update startup commands

## Troubleshooting

### Import errors
**Problem:** `ModuleNotFoundError: No module named 'data_loader'`

**Solution:** Update imports:
```python
# Old
from data_loader import DataLoader

# New
from ml.data.data_loader import DataLoader
```

### Model not found
**Problem:** Models not loading

**Solution:** Check paths in `config.yaml` and copy models:
```bash
cp -r models/* ml/model/saved_models/
```

### Port conflict
**Problem:** Port 5000 vs 8000

**Solution:** Update any hardcoded references:
- Old Flask default: 5000
- New FastAPI default: 8000

### Frontend not loading
**Problem:** 404 on static files

**Solution:** Ensure frontend files are in correct location:
```bash
ls frontend/static/
ls frontend/templates/
```

## Backward Compatibility

The old files are still in the root directory for reference. You can:

1. Keep them temporarily for comparison
2. Delete them once everything works
3. Use git to track changes

To clean up old files:
```bash
# After confirming new structure works
rm web_app.py
rm -rf templates/ static/ models/ feedback_data/
# Keep config.yaml (it's been updated)
```

## Questions?

Refer to:
- `PROJECT_README.md` - Complete project documentation
- `backend/README.md` - Backend API documentation
- `ml/README.md` - ML documentation
- API docs at `http://localhost:8000/docs`

