#!/bin/bash
# Development startup script with hot reload

echo "=================================="
echo "Intent Classification System (Dev)"
echo "=================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found! Run ./start.sh first."
    exit 1
fi

# Start server with auto-reload
echo "Starting FastAPI server in development mode..."
echo "API Documentation: http://localhost:8000/docs"
echo "Auto-reload enabled"
echo "Press Ctrl+C to stop"
echo ""

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

