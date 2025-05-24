# AI Tutor

An AI-powered tutoring system to replace live Python lectures with personalized, multilingual teaching capabilities.

## Project Overview

This AI Tutor system provides:
- **Multilingual Teaching**: Supports teaching in any language requested by students
- **Curriculum-Controlled Learning**: Pre-set lecture → topic → sub-topic sequences
- **Student Progress Tracking**: Green/Yellow/Red status tracking per topic
- **Automatic Note Generation**: Converts tutoring conversations into structured notes
- **Admin Dashboard**: Instructor view of student progress and struggle points

## Project Structure

```
ai-tutor/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Backend dependencies
│   ├── start_backend.sh    # Backend startup script
│   └── .venv/              # Backend virtual environment
├── frontend/               # Streamlit frontend
│   ├── main.py             # Streamlit application
│   ├── requirements.txt    # Frontend dependencies
│   ├── start_frontend.sh   # Frontend startup script
│   └── .venv/              # Frontend virtual environment
├── docs/                   # Documentation
├── tests/                  # Test files
├── env.example             # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: SQLite (development), PostgreSQL (production)
- **LLM**: GPT-4o-mini
- **Package Manager**: UV
- **Vector DB**: pgvector (future)

## Development Setup

### Prerequisites

- Python 3.11+
- UV package manager
- Git
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-tutor
```

2. Copy environment configuration:
```bash
cp env.example .env
# Edit .env with your actual OpenAI API key
```

3. Set up backend:
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

4. Set up frontend:
```bash
cd ../frontend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### Running the Application

#### Option 1: Using Individual Startup Scripts (Recommended)

1. **Start the backend** (in one terminal):
```bash
cd backend
./start_backend.sh
```

2. **Start the frontend** (in another terminal):
```bash
cd frontend
./start_frontend.sh
```

#### Option 2: Manual Startup

1. **Start the backend** (in one terminal):
```bash
cd backend
source .venv/bin/activate
python main.py
```

2. **Start the frontend** (in another terminal):
```bash
cd frontend
source .venv/bin/activate
streamlit run main.py --server.port 8501
```

### Access Points

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Development Phases

### P0: Hello-world Chat Tutor (Current)
- ✅ Single student, single topic
- ✅ Text-based conversation (no speech)
- ✅ Basic LLM integration
- ✅ Simple Streamlit UI
- ✅ FastAPI backend with OpenAI integration

### P1: Curriculum Engine + Notes
- Database schema implementation
- Admin curriculum upload
- Auto-note generation

### P2: Progress Tracking & Dashboard
- G/Y/R status logic
- Heat-map dashboards
- CSV export functionality

### P3: Multi-student Concurrency
- Authentication system
- Session isolation
- Redis scaling

## Features (P0)

### Backend (FastAPI)
- RESTful API endpoints for chat functionality
- OpenAI GPT-4o-mini integration
- CORS enabled for frontend communication
- In-memory conversation storage
- Health check endpoints
- Automatic API documentation

### Frontend (Streamlit)
- Clean, modern chat interface
- Topic and language selection
- Real-time API status monitoring
- Session state management
- Progress tracking metrics
- Example questions and tips

### Configuration
- Environment-based configuration
- Separate virtual environments for isolation
- Easy-to-use startup scripts
- Comprehensive logging

## Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
API_HOST=localhost
API_PORT=8000
STREAMLIT_PORT=8501
LLM_MODEL=gpt-4o-mini
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7
DEFAULT_LANGUAGE=en
DEFAULT_TOPIC=Python Basics
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[License information to be added]

