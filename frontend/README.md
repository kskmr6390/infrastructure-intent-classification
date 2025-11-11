# Frontend

This directory contains the web interface for the Intent Classification System.

## Structure

```
frontend/
├── static/
│   ├── css/          # Stylesheets
│   │   └── style.css
│   └── js/           # JavaScript files
│       └── app.js
└── templates/        # HTML templates
    └── chat.html
```

## Features

- Modern chat interface
- Real-time intent predictions
- Session management
- Feedback submission
- Visualization of confidence scores

## Usage

The frontend is served by the FastAPI backend. Access it at:
- Main interface: `http://localhost:8000/`
- Static files: `http://localhost:8000/static/`

## Technology Stack

- HTML5
- CSS3
- Vanilla JavaScript
- Responsive design

## Development

To modify the frontend:
1. Edit HTML templates in `templates/`
2. Edit styles in `static/css/`
3. Edit JavaScript in `static/js/`
4. Refresh browser to see changes (FastAPI auto-reload in debug mode)

