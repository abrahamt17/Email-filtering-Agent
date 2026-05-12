#!/bin/bash
# Run the production server with gunicorn

set -e

echo "Starting AI Email Processing System (Production)..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Export environment for production
export ENVIRONMENT=production
export DEBUG=false

# Number of workers (default: 4, recommended: 2 * CPU + 1)
WORKERS=${WORKERS:-4}

# Run with gunicorn
gunicorn app.main:app \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --graceful-timeout 30 \
    --timeout 60

echo "Server stopped."
