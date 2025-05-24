#!/bin/bash

# AI Tutor Frontend Startup Script

echo "🎨 Starting AI Tutor Frontend (Streamlit)..."

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
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    uv pip install -r requirements.txt
fi

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend API is not running. Please start the backend first:"
    echo "   cd ../backend && ./start_backend.sh"
    echo ""
    echo "🔄 Continuing anyway (you can start backend later)..."
fi

# Start the Streamlit server
echo "🌟 Starting Streamlit server..."
echo "📱 Frontend will be available at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

streamlit run main.py --server.port 8501 