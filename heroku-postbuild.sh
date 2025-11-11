#!/bin/bash
# Post-build script for Heroku deployment
# This script runs after dependencies are installed

echo "Running post-build setup..."

# Create necessary directories
mkdir -p ml/model/saved_models
mkdir -p ml/data/feedback
mkdir -p backend/database
mkdir -p logs
mkdir -p observability_data

# Check if models exist
if [ ! -f ml/model/saved_models/*.pkl ] && [ ! -f ml/model/saved_models/*.pth ]; then
    echo "⚠️  Warning: No trained models found!"
    echo "Models should be trained locally and committed to the repository."
    echo "See guides/HEROKU_DEPLOYMENT.md for details."
fi

echo "Post-build setup complete!"

