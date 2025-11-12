# Heroku Slug Size Fix - Deployment Guide

## Problem
The Heroku slug was 4GB (exceeds 500MB limit) due to PyTorch and heavy ML libraries.

## Solution Applied

### 1. Lightweight Requirements
- **Production** (`requirements.txt`): Lightweight dependencies (~150MB)
  - Uses scikit-learn, numpy, pandas (no PyTorch)
  - Suitable for traditional ML model inference
  
- **Development** (`requirements-dev.txt`): Full dependencies including PyTorch
  - Use this for local development and training LLM models

### 2. Model Management
- **Included in Git**: Traditional ML models (90-310KB each)
  - `tfidf_svm_model_*.pkl`
  - `intent_mapping_*.pkl`
  - `label_encoder_*.pkl`

- **Excluded from Git/Slug**: LLM models (large)
  - LLM models remain in `.gitignore` and `.slugignore`

### 3. Application Behavior
- On Heroku: Uses **Traditional ML** predictor (scikit-learn)
  - Lightweight, fast, and accurate
  - No PyTorch dependencies needed
  
- Locally: Can use either Traditional ML or LLM predictor
  - LLM predictor falls back to Traditional ML if PyTorch unavailable

## Deployment Steps

### 1. Push Changes to Heroku
```bash
git push heroku main
```

### 2. Verify Deployment
The build should now succeed with a slug size under 500MB.

### 3. Test the Application
```bash
heroku open
# Or test the API
curl https://your-app.herokuapp.com/api/health
```

## Expected Slug Size
- **Before**: ~4GB (too large)
- **After**: ~200-250MB (well under 500MB limit)

## Local Development

### Install Full Dependencies (for training)
```bash
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Install Production Dependencies Only
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Performance Notes

Traditional ML (TF-IDF + SVM) performance:
- ✅ Fast inference (~10-50ms)
- ✅ Low memory footprint (~100MB)
- ✅ High accuracy (depends on training data)
- ✅ No GPU required

## Troubleshooting

### If deployment still fails
1. Check slug size: `heroku builds:info -a your-app-name`
2. Verify models are in repo: `git ls-files ml/model/saved_models/`
3. Check build logs: `heroku logs --tail -a your-app-name`

### If predictions fail
1. Verify models are loaded: Check `/api/health` endpoint
2. Check predictor type: Should show "traditional" not "llm"
3. Review application logs: `heroku logs --tail`

## Files Modified
- `.gitignore` - Allow traditional ML models
- `.slugignore` - Exclude LLM models only
- `requirements.txt` - Lightweight production dependencies
- `requirements-dev.txt` - Full development dependencies (new)
- Added 8 traditional ML model files to repository

## Next Steps
1. Push to Heroku: `git push heroku main`
2. Monitor build logs for success
3. Test the deployed application
4. Enjoy your working Heroku deployment! 🚀

