# Documentation

Complete documentation for the Intent Classification System.

## Available Guides

### Getting Started

#### [Quick Start](QUICK_START.md)
Get the system up and running in 5 minutes.
- Basic installation
- Training your first model
- Starting the server
- Testing predictions

#### [Setup Guide](SETUP_GUIDE.md)
Comprehensive installation and configuration guide.
- Prerequisites and dependencies
- Virtual environment setup
- Configuration options
- Troubleshooting common issues

#### [Usage Guide](USAGE_GUIDE.md)
How to use the system effectively.
- Web interface usage
- API integration
- Training and retraining models
- Self-learning features
- Feedback system

### Deployment

#### [Heroku Deployment Guide](HEROKU_DEPLOYMENT.md)
Complete guide for deploying to Heroku.
- Quick start (5 minutes)
- Step-by-step instructions
- Configuration options
- Troubleshooting
- Automated deployment script

## Quick Navigation

**New Users:** Start with [Quick Start](QUICK_START.md) → [Usage Guide](USAGE_GUIDE.md)

**Developers:** Read [Setup Guide](SETUP_GUIDE.md) → [Usage Guide](USAGE_GUIDE.md)

## Component Documentation

For detailed technical documentation, see:
- **Backend**: [../backend/README.md](../backend/README.md)
- **Frontend**: [../frontend/README.md](../frontend/README.md)
- **ML Models**: [../ml/README.md](../ml/README.md)
- **Data Handling**: [../ml/data/docs/](../ml/data/docs/)
- **Traditional ML**: [../ml/traditional_ml/docs/](../ml/traditional_ml/docs/)
- **LLM Models**: [../ml/llm/docs/](../ml/llm/docs/)

## Quick Commands

```bash
# Train a model
./train_model.sh

# Start production server
./start.sh

# Start development server
./start_dev.sh

# View API documentation
open http://localhost:8000/docs
```

## Getting Help

1. Check the relevant guide above
2. Visit API documentation at http://localhost:8000/docs
3. Review component-specific READMEs
4. Check troubleshooting section in [Setup Guide](SETUP_GUIDE.md)

---

**Return to:** [Main README](../README.md)
