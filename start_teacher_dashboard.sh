#!/bin/bash

# AI Tutor - Teacher Dashboard Startup Script
echo "🎓 Starting AI Tutor Teacher Dashboard..."

# Check if we're in the right directory
if [ ! -f "frontend/teacher_dashboard.py" ]; then
    echo "❌ Error: frontend/teacher_dashboard.py not found. Please run from project root."
    exit 1
fi

# Activate frontend virtual environment
echo "🔧 Setting up teacher dashboard environment..."
cd frontend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Frontend virtual environment not found."
    echo "Please run ./start_frontend.sh first to set up the environment."
    exit 1
fi

source venv/bin/activate

# Install any additional requirements if needed
pip install -r requirements.txt > /dev/null 2>&1

# Start the teacher dashboard
echo "🚀 Starting Teacher Dashboard on http://localhost:8502"
echo "📚 Use this interface to design and manage your AI curriculum"
echo ""
echo "👩‍🏫 Teacher Dashboard Features:"
echo "  • 📊 Analytics: View student engagement and progress"
echo "  • 🏗️ Curriculum Builder: Create lectures, topics, and subtopics"
echo "  • 🤖 AI Prompt Engineering: Define how AI teaches each concept"
echo "  • 📝 Code Examples: Add interactive learning materials"
echo ""
echo "Press Ctrl+C to stop the teacher dashboard"
echo "----------------------------------------"

streamlit run teacher_dashboard.py --server.port=8502 --server.address=localhost 