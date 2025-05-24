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
├── backend/          # FastAPI backend
├── frontend/         # Streamlit frontend
├── docs/            # Documentation
├── tests/           # Test files
├── env.example      # Environment variables template
├── .gitignore       # Git ignore rules
└── README.md        # This file
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

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-tutor
```

2. Copy environment configuration:
```bash
cp env.example .env
# Edit .env with your actual configuration values
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

1. Start the backend:
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

2. Start the frontend:
```bash
cd frontend
source .venv/bin/activate
streamlit run main.py --server.port 8501
```

## Development Phases

### P0: Hello-world Chat Tutor (Current)
- Single student, single topic
- Text-based conversation (no speech)
- Basic LLM integration
- Simple Streamlit UI

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[License information to be added]

