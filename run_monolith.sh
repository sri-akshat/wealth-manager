#!/bin/bash

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR"
export DATABASE_URL="postgresql://user:password@localhost:5432/userdb"
export INVESTMENT_DATABASE_URL="postgresql://user:password@localhost:5433/investmentdb"
export JWT_SECRET_KEY="your_secret_key_here"
export SECRET_KEY="your-secret-key-here"

# Run the server
cd "$SCRIPT_DIR"
uvicorn services.main:app --reload --port 8000 