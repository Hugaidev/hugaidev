#!/bin/bash

echo "📦 Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "📚 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "🎨 Setting up Cairo library path for SVG support..."
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

echo "http://127.0.0.1:8000/"
mkdocs serve -f mkdocs.yml 

