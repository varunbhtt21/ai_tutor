#!/bin/bash

# AI Tutor Backend Startup Script

echo "🚀 Starting AI Tutor Backend (FastAPI)..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run 'uv venv' first."
    exit 1
fi

# Check if .env file exists in root directory
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found in root directory."
    if [ ! -f "../env.example" ]; then
        echo "❌ env.example file not found in root directory."
        exit 1
    fi
    echo "📝 Creating .env file from template..."
    cp ../env.example ../.env
    echo "✅ Created .env file from template."
    echo "🔑 Please edit ../.env and add your OPENAI_API_KEY before running again."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    uv pip install -r requirements.txt
fi

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
echo "📱 Backend API will be available at: http://localhost:8000"
echo "📚 API Documentation will be available at: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python main.py 