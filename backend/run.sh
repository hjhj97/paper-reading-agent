#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run FastAPI server
uvicorn app.main:app --reload --port 8000

