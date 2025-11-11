# Backend

FastAPI-based backend for the Intent Classification System.

## Structure

```
backend/
├── api/              # API endpoints
│   ├── chat.py       # Chat endpoints
│   ├── sessions.py   # Session management
│   ├── feedback.py   # Feedback endpoints
│   └── health.py     # Health checks
├── core/             # Core modules
│   ├── config.py     # Configuration management
│   └── predictor.py  # ML predictor manager
├── database/         # Database layer
│   └── db.py         # SQLite database operations
└── main.py           # FastAPI application entry point
```

## API Endpoints

### Health
- `GET /api/health` - Health check and model status

### Chat
- `POST /api/chat` - Process chat message and get intent prediction

### Sessions
- `GET /api/sessions` - Get all sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/{id}` - Get session details
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session

### Feedback
- `POST /api/feedback` - Submit feedback
- `GET /api/statistics` - Get statistics
- `GET /api/export_feedback` - Export feedback data

## Running the Backend

```bash
# From project root
python -m backend.main

# Or with uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

FastAPI provides automatic interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration

Configuration is managed through:
1. `config.yaml` - ML model configuration
2. `.env` - Environment variables (optional)
3. `backend/core/config.py` - Application settings

## Development

- FastAPI auto-reloads on code changes in debug mode
- Use type hints for better IDE support
- Pydantic models for request/response validation
- Async/await for better performance

