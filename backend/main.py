import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import logging
from typing import List, Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Tutor Backend",
    description="Backend API for AI Tutor system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    student_id: str = "default_student"
    topic: str = "Python Basics"
    language: str = "en"

class ChatResponse(BaseModel):
    response: str
    topic: str
    understanding_level: Optional[str] = None

# In-memory storage for P0 (will be replaced with database in P1)
conversation_history = {}

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "AI Tutor Backend is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-tutor-backend"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """Main chat endpoint for interacting with the AI tutor."""
    try:
        # Get or initialize conversation history for this student
        if request.student_id not in conversation_history:
            conversation_history[request.student_id] = []

        # Add user message to history
        conversation_history[request.student_id].append({
            "role": "user",
            "content": request.message
        })

        # Build system prompt for the tutor
        system_prompt = f"""You are "Python Pro Tutor", an expert Python programming instructor.

You are currently teaching: {request.topic}
Student's preferred language: {request.language}

Your teaching approach:
1. Be encouraging and patient
2. Explain concepts in simple terms
3. Use practical examples
4. Ask questions to check understanding
5. Adapt to the student's language preference
6. Focus specifically on {request.topic}

After each explanation, ask the student to rate their understanding on a scale of 1-3:
- 1: Not clear, need more explanation
- 2: Somewhat clear, but have some questions  
- 3: Very clear, ready to move on

Keep your responses concise but comprehensive."""

        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history (last 10 messages to stay within token limits)
        recent_history = conversation_history[request.student_id][-10:]
        messages.extend(recent_history)

        # Get response from OpenAI
        response = openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )

        tutor_response = response.choices[0].message.content

        # Add tutor response to history
        conversation_history[request.student_id].append({
            "role": "assistant", 
            "content": tutor_response
        })

        # Simple understanding level detection (will be enhanced in P2)
        understanding_level = None
        if any(word in request.message.lower() for word in ["don't understand", "confused", "unclear"]):
            understanding_level = "needs_help"
        elif any(word in request.message.lower() for word in ["got it", "clear", "understand"]):
            understanding_level = "understood"

        return ChatResponse(
            response=tutor_response,
            topic=request.topic,
            understanding_level=understanding_level
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/conversation/{student_id}")
async def get_conversation_history(student_id: str):
    """Get conversation history for a student."""
    if student_id not in conversation_history:
        return {"conversation": []}
    
    return {"conversation": conversation_history[student_id]}

@app.delete("/conversation/{student_id}")
async def clear_conversation_history(student_id: str):
    """Clear conversation history for a student."""
    if student_id in conversation_history:
        conversation_history[student_id] = []
    
    return {"message": "Conversation history cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("API_HOST", "localhost"), 
        port=int(os.getenv("API_PORT", "8000")), 
        reload=True
    ) 