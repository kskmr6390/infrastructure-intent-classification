# Heroku Deployment Guide

Complete guide to deploy your Intent Classification System to Heroku.

## Quick Start (5 Minutes)

```bash
# 1. Train models
source venv/bin/activate
python -m ml.traditional_ml.train

# 2. Update .gitignore - comment out these lines:
#    # ml/model/saved_models/*.pkl
#    # ml/model/saved_models/*.pth

# 3. Commit models
git add ml/model/saved_models/
git commit -m "Add trained models for Heroku"

# 4. Deploy
heroku login
heroku create your-app-name
git push heroku main
heroku ps:scale web=1
heroku open
```

Or use the automated script:

```bash
./deploy_to_heroku.sh
```

## Prerequisites

- **Heroku Account**: [Sign up free](https://signup.heroku.com/)
- **Heroku CLI**: [Install here](https://devcenter.heroku.com/articles/heroku-cli)
- **Git repository**: Your project must be in Git
- **Trained models**: See below

## Step-by-Step Deployment

### 1. Install Heroku CLI

```bash
# Mac
brew tap heroku/brew && brew install heroku

# Or download from: https://devcenter.heroku.com/articles/heroku-cli
```

### 2. Train Models Locally

**IMPORTANT**: Heroku has limited build time. Train models locally first.

```bash
source venv/bin/activate
python -m ml.traditional_ml.train  # Recommended: ~50MB, fast
```

### 3. Update .gitignore

Your models must be in Git. Edit `.gitignore` and comment out:

```gitignore
# ML Models
# ml/model/saved_models/*.pkl    ← Add # at start
# ml/model/saved_models/*.pth
# ml/model/saved_models/*.h5
```

Or force add models:

```bash
git add -f ml/model/saved_models/*.pkl
```

### 4. Commit Everything

```bash
git add .
git commit -m "Prepare for Heroku deployment"
```

### 5. Login to Heroku

```bash
heroku login
```

### 6. Create Heroku App

```bash
# With custom name
heroku create your-app-name

# Or auto-generate name
heroku create
```

### 7. Configure Environment Variables (Optional)

```bash
# Set DEBUG to false
heroku config:set DEBUG=false

# If using LangSmith
heroku config:set LANGCHAIN_TRACING_V2=true
heroku config:set LANGCHAIN_API_KEY=your_key
heroku config:set LANGCHAIN_PROJECT=intent-classification
```

### 8. Deploy

```bash
git push heroku main

# If on different branch:
git push heroku your-branch:main
```

### 9. Scale Dyno

```bash
heroku ps:scale web=1
```

### 10. Open Your App

```bash
heroku open
```

Your app is now live at `https://your-app-name.herokuapp.com`!

## Configuration

### Recommended config.yaml for Heroku

```yaml
model:
  type: "tfidf_svm"  # Lightweight, fast, 50MB

self_learning:
  enabled: false     # Requires persistent storage

observability:
  local_observability:
    enabled: false   # Use LangSmith or external service
  langsmith:
    enabled: true    # Set LANGCHAIN_API_KEY in Heroku
```

### Dyno Types

| Type | RAM | Cost | Use Case |
|------|-----|------|----------|
| Hobby | 512MB | $7/mo | Small apps, demos |
| Standard-1X | 512MB | $25/mo | Production |
| Standard-2X | 1GB | $50/mo | Large models |

Upgrade dyno:
```bash
heroku ps:type standard-1x
```

## Important Limitations

### 1. Ephemeral Filesystem ⚠️

Heroku's filesystem resets on restart. This affects:
- ❌ Feedback data won't persist
- ❌ Self-learning won't work
- ❌ SQLite databases reset
- ❌ Logs disappear

**Solutions:**
- Use PostgreSQL: `heroku addons:create heroku-postgresql:mini`
- Use S3 for file storage
- Disable self-learning (see config.yaml above)

### 2. Slug Size Limit (500MB)

Choose models wisely:
- ✅ TF-IDF + SVM: ~50MB (recommended)
- ✅ Sentence Transformer: ~150MB
- ❌ Fine-tuned LLM: 500MB+ (too large)

### 3. Memory Limits

Monitor memory with: `heroku logs --tail | grep R14`

If you see R14 errors (memory exceeded):
```bash
heroku ps:type standard-2x
```

## Useful Commands

```bash
# View logs
heroku logs --tail

# Check status
heroku ps

# View config
heroku config

# Restart app
heroku restart

# Run commands
heroku run bash
heroku run python -m ml.traditional_ml.train

# Rollback deployment
heroku releases
heroku rollback

# Delete app
heroku apps:destroy your-app-name
```

## Testing Your Deployment

```bash
# Health check
curl https://your-app-name.herokuapp.com/api/health

# Test prediction
curl -X POST https://your-app-name.herokuapp.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "What is the CPU usage?"}'

# Open in browser
heroku open
```

## Troubleshooting

### "No trained models found"

```bash
python -m ml.traditional_ml.train
git add ml/model/saved_models/
git commit -m "Add models"
git push heroku main
```

### "Application Error" (H10)

```bash
heroku logs --tail  # Check for errors
```

Common causes:
- Missing models in Git
- Wrong Python version
- Missing dependencies

### "Slug size too large"

```bash
# Use smaller model in config.yaml
model:
  type: "tfidf_svm"

# Check size
du -sh ml/model/saved_models/
```

### "Memory quota exceeded" (R14)

```bash
# Upgrade dyno
heroku ps:type standard-1x

# Or use smaller model
```

## Environment Variables

Set on Heroku:

```bash
heroku config:set VARIABLE_NAME=value
```

Available variables:
- `DEBUG` - Set to `false` for production
- `LANGCHAIN_TRACING_V2` - Enable LangSmith
- `LANGCHAIN_API_KEY` - Your LangSmith API key
- `LANGCHAIN_PROJECT` - Project name
- `PORT` - Auto-set by Heroku (don't override)

## Automated Deployment

Use the included script for automatic deployment:

```bash
./deploy_to_heroku.sh
```

This script:
- ✓ Checks prerequisites
- ✓ Verifies models are trained
- ✓ Creates Heroku app if needed
- ✓ Configures environment
- ✓ Deploys your app
- ✓ Opens in browser

## Production Checklist

Before going live:

- [ ] Train production models
- [ ] Commit models to Git
- [ ] Set `DEBUG=false`
- [ ] Configure proper CORS origins
- [ ] Set up PostgreSQL if persisting data
- [ ] Configure LangSmith for observability
- [ ] Test all API endpoints
- [ ] Monitor logs for errors
- [ ] Set up custom domain (optional)

## Cost Estimate

**Minimal Setup (Testing):**
- Hobby Dyno: $7/month
- **Total: $7/month**

**Production Setup:**
- Standard-1X Dyno: $25/month
- PostgreSQL Mini: $9/month
- **Total: $34/month**

## CI/CD with GitHub

1. Go to Heroku Dashboard
2. Select your app → Deploy
3. Connect GitHub repository
4. Enable "Automatic deploys from main"

Every push to main will auto-deploy!

## Resources

- [Heroku Python Docs](https://devcenter.heroku.com/categories/python-support)
- [Heroku CLI Reference](https://devcenter.heroku.com/articles/heroku-cli-commands)
- [Heroku Status](https://status.heroku.com/)

## Support

- Check logs: `heroku logs --tail`
- View app status: `heroku ps`
- Visit: [Heroku Dev Center](https://devcenter.heroku.com/)

---

**Ready to deploy?** Run `./deploy_to_heroku.sh` or follow the Quick Start above!

