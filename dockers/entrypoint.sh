#!/bin/bash

set -e

echo "Starting MCP weather..."
#python -m uvicorn --app-dir /app/src --host 0.0.0.0  --port ${APP_PORT:-8000} main:app
python src/weather.py http