#!/bin/bash
# Run the development server

set -e

echo "Starting AI Email Processing System..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Export environment for development
export ENVIRONMENT=development
export DEBUG=true

# Run the server with auto-reload
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info

echo "Server stopped."
