#!/bin/bash

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR"

# Run the server
cd "$SCRIPT_DIR"
uvicorn services.main:app --reload --port 8000 