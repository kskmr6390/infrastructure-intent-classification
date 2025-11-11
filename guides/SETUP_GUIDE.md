# Setup Guide

Complete setup guide for the Intent Classification System.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for version control)
- Docker (optional, for containerized deployment)

## Installation Methods

### Method 1: Quick Start (Recommended for First Time)

```bash
# Clone or navigate to project
cd intent_classification

# Run the setup script
chmod +x start.sh train_model.sh
./train_model.sh
./start.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Train a model
4. Start the server

Access at: `http://localhost:8000`

### Method 2: Step-by-Step Installation

#### 1. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

#### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Verify Installation

```bash
python -c "import fastapi, torch, sklearn; print('All dependencies installed!')"
```

#### 4. Configure Environment (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit as needed
nano .env
```

#### 5. Prepare Data

Ensure your dataset is in the correct location:

```bash
# Dataset should be at:
ml/data/raw/infra_copilot_intent_dataset_v2.jsonl

# Or update config.yaml with your dataset path
```

#### 6. Train a Model

Choose one:

```bash
# Option A: Traditional ML (Fast - 1-2 minutes)
python -m ml.traditional_ml.train

# Option B: LLM-based (Better accuracy - 5-10 minutes)
python -m ml.llm.train_llm

# Option C: Both
python -m ml.traditional_ml.train
python -m ml.llm.train_llm
```

#### 7. Start the Server

```bash
# Production mode
python -m backend.main

# Development mode (auto-reload)
./start_dev.sh
# OR
uvicorn backend.main:app --reload
```

#### 8. Verify Server

Open browser:
- Main interface: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### Method 3: Docker Installation

#### Using Docker Compose (Easiest)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Using Docker Directly

```bash
# Build image
docker build -t intent-classification .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/ml/model/saved_models:/app/ml/model/saved_models \
  -v $(pwd)/ml/data:/app/ml/data \
  intent-classification
```

**Note:** You need to train models before running Docker, or mount a volume with trained models.

## Configuration

### 1. ML Configuration (`config.yaml`)

Main configuration file for ML models:

```yaml
model:
  type: "tfidf_svm"  # or "llm", "hybrid"
  
data:
  dataset_path: "ml/data/raw/your_dataset.jsonl"
  train_test_split: 0.8
```

Key sections:
- `data`: Dataset and preprocessing settings
- `model`: Model type and hyperparameters
- `training`: Training configuration
- `inference`: Prediction settings

### 2. Environment Variables (`.env`)

Optional, for deployment:

```bash
DEBUG=false
HOST=0.0.0.0
PORT=8000
DATABASE_PATH=backend/database/chat_sessions.db
```

### 3. Application Settings

Modify in `backend/core/config.py` if needed:
- CORS origins
- File paths
- Logging configuration

## Verification

### 1. Check Installation

```bash
# Check Python version
python --version  # Should be 3.9+

# Check key packages
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import sklearn; print(f'Scikit-learn: {sklearn.__version__}')"
```

### 2. Check Project Structure

```bash
# Should see these directories
ls -la
# frontend/ backend/ ml/ config.yaml requirements.txt
```

### 3. Check Trained Models

```bash
ls -la ml/model/saved_models/
# Should see .pkl files
```

### 4. Test API

```bash
# Health check
curl http://localhost:8000/api/health

# Test prediction
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "What is CPU usage?"}'
```

## Common Setup Issues

### Issue: Python version too old

```bash
# Install Python 3.9+
# On Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv

# On Mac (with Homebrew)
brew install python@3.9
```

### Issue: pip install fails

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install build tools (Linux)
sudo apt install build-essential python3-dev

# Try installing problematic packages individually
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### Issue: Out of memory during training

```yaml
# In config.yaml, reduce:
model:
  llm:
    batch_size: 8  # Reduce from 16
    max_length: 64  # Reduce from 128
```

### Issue: Port already in use

```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
PORT=8001 python -m backend.main
```

### Issue: Module not found

```bash
# Ensure you're in project root
pwd

# Reinstall in editable mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: CORS errors in browser

In `backend/core/config.py`:

```python
CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
```

### Issue: Models not loading

```bash
# Check model files exist
ls ml/model/saved_models/

# Retrain if needed
python -m ml.traditional_ml.train

# Check paths in config.yaml
grep -A 5 "training:" config.yaml
```

## Development Setup

For active development:

```bash
# Install dev dependencies
pip install black isort flake8 pytest

# Format code
black .
isort .

# Lint
flake8 .

# Run tests
pytest
```

## Production Setup

Additional steps for production:

1. **Disable debug mode:**
   ```bash
   DEBUG=false
   ```

2. **Use production server:**
   ```bash
   # With multiple workers
   uvicorn backend.main:app \
     --host 0.0.0.0 \
     --port 8000 \
     --workers 4 \
     --no-access-log
   ```

3. **Setup reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Setup systemd service:**
   ```ini
   [Unit]
   Description=Intent Classification API
   After=network.target
   
   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/project
   ExecStart=/path/to/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Setup logging:**
   ```yaml
   logging:
     level: "WARNING"  # Less verbose
     log_file: "/var/log/intent-classification/app.log"
   ```

6. **Setup monitoring:**
   - Use Prometheus + Grafana
   - Enable health checks
   - Set up alerts

## Next Steps

After successful setup:

1. **Explore the API:**
   - Visit `http://localhost:8000/docs`
   - Try different intents
   - Submit feedback

2. **Customize the model:**
   - Edit `config.yaml`
   - Add your own training data
   - Retrain with new settings

3. **Integrate with your app:**
   - Use the REST API
   - Integrate authentication
   - Add custom intents

4. **Read the docs:**
   - `PROJECT_README.md` - Overview
   - `backend/README.md` - API docs
   - `ml/README.md` - ML docs

## Getting Help

If you encounter issues:

1. Check this guide
2. Check `MIGRATION_GUIDE.md` if upgrading
3. Review error logs in `logs/`
4. Check API docs at `/docs`
5. Open an issue on GitHub

## Success Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Dataset in correct location
- [ ] Model trained successfully
- [ ] Server starts without errors
- [ ] Can access web interface
- [ ] API endpoints responding
- [ ] Health check passes
- [ ] Can make predictions

If all checked, you're ready to go! 🚀

