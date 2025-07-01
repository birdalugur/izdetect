#!/bin/bash
set -e

# Check if we're running the API service
if [ "$1" = "api" ]; then
    echo "Starting API service..."
    cd /app/api
    uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
# Check if we're running the services
elif [ "$1" = "services" ]; then
    echo "Starting object detection services..."
    cd /app/services
    python3 main.py
else
    echo "Please specify a service to run: api or services"
    exit 1
fi