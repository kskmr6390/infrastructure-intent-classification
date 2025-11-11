#!/bin/bash
# Startup script for Intent Classification System

echo "=================================="
echo "Intent Classification System"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p ml/data/raw ml/data/processed ml/data/feedback
mkdir -p ml/model/saved_models
mkdir -p backend/database
mkdir -p logs
mkdir -p frontend/static/css frontend/static/js frontend/templates

# Check if models exist
if [ ! -f "ml/model/saved_models/*.pkl" ]; then
    echo ""
    echo "⚠️  Warning: No trained models found!"
    echo "Please train a model first:"
    echo "  python -m ml.traditional_ml.train"
    echo "  OR"
    echo "  python -m ml.llm.train_llm"
    echo ""
fi

# Start the server
echo ""
echo "Starting FastAPI server..."
echo "API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

python -m backend.main

