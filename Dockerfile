# Multi-stage Dockerfile for Intent Classification System

# Stage 1: Base Python image with dependencies
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Application
FROM base as app

WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p ml/data/raw ml/data/processed ml/data/feedback \
    ml/model/saved_models \
    backend/database \
    logs \
    frontend/static frontend/templates

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["python", "-m", "backend.main"]

