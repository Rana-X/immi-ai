#!/usr/bin/env bash
set -e

# Print debug information
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

# Navigate to the backend directory
cd "$(dirname "$0")"
echo "Changed to backend directory: $(pwd)"
echo "Backend directory contents: $(ls -la)"

# Start the application
echo "Starting uvicorn server..."
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} 