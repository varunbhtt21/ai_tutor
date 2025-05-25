import os
import time
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

# Import our new modules
from database import get_db, create_tables
from ai_tutor_service import AITutorService
from curriculum_seed import seed_database
from teacher_service import TeacherCurriculumService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Tutor Backend - P1",
    description="Curriculum-driven AI tutoring system with structured learning paths",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:8502"],  # Student frontend + Teacher dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models for API
class LearningSessionRequest(BaseModel):
    student_id: str
    language: str = "en"

class StudentResponseRequest(BaseModel):
    student_id: str
    message: str
    language: str = "en"

class LearningSessionResponse(BaseModel):
    type: str  # "introduction", "continuation", "response", "error"
    message: str
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    lecture: Optional[str] = None
    understanding_level: Optional[str] = None
    next_action: Optional[str] = None
    progress: Optional[dict] = None

# Legacy models for backward compatibility
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

# Teacher Dashboard Models
class LectureCreate(BaseModel):
    title: str
    description: str
    order_index: int

class LectureUpdate(BaseModel):
    title: str
    description: str
    order_index: int
    is_active: bool

class TopicCreate(BaseModel):
    lecture_id: int
    title: str
    description: str
    order_index: int
    learning_objectives: List[str]
    estimated_duration_minutes: int = 30

class TopicUpdate(BaseModel):
    title: str
    description: str
    order_index: int
    learning_objectives: List[str]
    estimated_duration_minutes: int

class SubTopicCreate(BaseModel):
    topic_id: int
    title: str
    content: str
    order_index: int
    examples: List[dict] = []
    exercises: List[dict] = []
    introduction_prompt: Optional[str] = None
    explanation_prompt: Optional[str] = None
    assessment_prompt: Optional[str] = None

class SubTopicUpdate(BaseModel):
    title: str
    content: str
    order_index: int
    examples: List[dict] = []
    exercises: List[dict] = []
    introduction_prompt: Optional[str] = None
    explanation_prompt: Optional[str] = None
    assessment_prompt: Optional[str] = None

class ReorderRequest(BaseModel):
    items: List[dict]  # [{"id": 1, "order_index": 1}, ...]

class DuplicateLectureRequest(BaseModel):
    source_lecture_id: int
    new_title: str

@app.on_event("startup")
async def startup_event():
    """Initialize database and seed curriculum on startup"""
    try:
        # Create database tables
        create_tables()
        logger.info("✅ Database tables created")
        
        # Seed curriculum data
        seed_database()
        logger.info("✅ Curriculum data seeded")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "AI Tutor Backend P1 is running! 🚀", "version": "1.1.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-tutor-backend-p1", "version": "1.1.0"}

# New P1 Curriculum-Driven Endpoints

@app.post("/learning/start", response_model=LearningSessionResponse)
async def start_learning_session(request: LearningSessionRequest, db: Session = Depends(get_db)):
    """Start or continue a curriculum-driven learning session"""
    try:
        # Create AI tutor service
        ai_tutor = AITutorService(openai_client, db)
        
        # Initiate learning session
        start_time = time.time()
        result = ai_tutor.initiate_learning_session(request.student_id, request.language)
        response_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Learning session started for {request.student_id}, response time: {response_time}ms")
        
        return LearningSessionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error starting learning session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/learning/respond", response_model=LearningSessionResponse)
async def process_student_response(request: StudentResponseRequest, db: Session = Depends(get_db)):
    """Process student response in curriculum-driven conversation"""
    try:
        # Create AI tutor service
        ai_tutor = AITutorService(openai_client, db)
        
        # Process student response
        start_time = time.time()
        result = ai_tutor.process_student_response(request.student_id, request.message, request.language)
        response_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Processed response for {request.student_id}, understanding: {result.get('understanding_level')}, response time: {response_time}ms")
        
        return LearningSessionResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing student response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/student/{student_id}/progress")
async def get_student_progress(student_id: str, db: Session = Depends(get_db)):
    """Get detailed progress information for a student"""
    try:
        ai_tutor = AITutorService(openai_client, db)
        student = ai_tutor.get_or_create_student(student_id)
        progress = ai_tutor._get_progress_summary(student)
        
        return {
            "student_id": student_id,
            "current_lecture": student.current_lecture.title if student.current_lecture else None,
            "progress": progress
        }
        
    except Exception as e:
        logger.error(f"Error fetching progress for {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/curriculum/lectures")
async def get_curriculum_structure(db: Session = Depends(get_db)):
    """Get the curriculum structure for admin/debugging purposes"""
    try:
        from database import Lecture, Topic, SubTopic
        
        lectures = db.query(Lecture).order_by(Lecture.order_index).all()
        
        result = []
        for lecture in lectures:
            topics = []
            for topic in sorted(lecture.topics, key=lambda t: t.order_index):
                subtopics = [
                    {
                        "id": st.id,
                        "title": st.title,
                        "order_index": st.order_index
                    }
                    for st in sorted(topic.subtopics, key=lambda st: st.order_index)
                ]
                
                topics.append({
                    "id": topic.id,
                    "title": topic.title,
                    "description": topic.description,
                    "order_index": topic.order_index,
                    "estimated_duration_minutes": topic.estimated_duration_minutes,
                    "subtopics": subtopics
                })
            
            result.append({
                "id": lecture.id,
                "title": lecture.title,
                "description": lecture.description,
                "order_index": lecture.order_index,
                "topics": topics
            })
        
        return {"lectures": result}
        
    except Exception as e:
        logger.error(f"Error fetching curriculum: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Teacher Dashboard Endpoints

@app.get("/teacher/curriculum")
async def get_full_curriculum(db: Session = Depends(get_db)):
    """Get complete curriculum structure for teacher dashboard"""
    try:
        teacher_service = TeacherCurriculumService(db)
        curriculum = teacher_service.get_full_curriculum_structure()
        return curriculum
    except Exception as e:
        logger.error(f"Error fetching curriculum structure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/teacher/analytics")
async def get_curriculum_analytics(db: Session = Depends(get_db)):
    """Get curriculum usage analytics"""
    try:
        teacher_service = TeacherCurriculumService(db)
        analytics = teacher_service.get_curriculum_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# LECTURE MANAGEMENT
@app.post("/teacher/lectures")
async def create_lecture(request: LectureCreate, db: Session = Depends(get_db)):
    """Create a new lecture"""
    try:
        teacher_service = TeacherCurriculumService(db)
        lecture = teacher_service.create_lecture(
            title=request.title,
            description=request.description,
            order_index=request.order_index
        )
        
        return {
            "id": lecture.id,
            "title": lecture.title,
            "description": lecture.description,
            "order_index": lecture.order_index,
            "is_active": lecture.is_active,
            "message": "Lecture created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating lecture: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/teacher/lectures/{lecture_id}")
async def update_lecture(lecture_id: int, request: LectureUpdate, db: Session = Depends(get_db)):
    """Update lecture details"""
    try:
        teacher_service = TeacherCurriculumService(db)
        lecture = teacher_service.update_lecture(
            lecture_id=lecture_id,
            title=request.title,
            description=request.description,
            order_index=request.order_index,
            is_active=request.is_active
        )
        
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        return {
            "id": lecture.id,
            "title": lecture.title,
            "description": lecture.description,
            "order_index": lecture.order_index,
            "is_active": lecture.is_active,
            "message": "Lecture updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lecture: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/teacher/lectures/{lecture_id}")
async def delete_lecture(lecture_id: int, db: Session = Depends(get_db)):
    """Delete lecture and all related content"""
    try:
        teacher_service = TeacherCurriculumService(db)
        success = teacher_service.delete_lecture(lecture_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        return {"message": "Lecture deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lecture: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/teacher/lectures/reorder")
async def reorder_lectures(request: ReorderRequest, db: Session = Depends(get_db)):
    """Reorder lectures"""
    try:
        teacher_service = TeacherCurriculumService(db)
        success = teacher_service.reorder_lectures(request.items)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reorder lectures")
        
        return {"message": "Lectures reordered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering lectures: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/teacher/lectures/duplicate")
async def duplicate_lecture(request: DuplicateLectureRequest, db: Session = Depends(get_db)):
    """Duplicate an entire lecture with all content"""
    try:
        teacher_service = TeacherCurriculumService(db)
        new_lecture = teacher_service.duplicate_curriculum_structure(
            source_lecture_id=request.source_lecture_id,
            new_title=request.new_title
        )
        
        if not new_lecture:
            raise HTTPException(status_code=404, detail="Source lecture not found")
        
        return {
            "id": new_lecture.id,
            "title": new_lecture.title,
            "message": "Lecture duplicated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating lecture: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# TOPIC MANAGEMENT
@app.post("/teacher/topics")
async def create_topic(request: TopicCreate, db: Session = Depends(get_db)):
    """Create a new topic"""
    try:
        teacher_service = TeacherCurriculumService(db)
        topic = teacher_service.create_topic(
            lecture_id=request.lecture_id,
            title=request.title,
            description=request.description,
            order_index=request.order_index,
            learning_objectives=request.learning_objectives,
            estimated_duration_minutes=request.estimated_duration_minutes
        )
        
        if not topic:
            raise HTTPException(status_code=404, detail="Lecture not found")
        
        return {
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "message": "Topic created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/teacher/topics/{topic_id}")
async def update_topic(topic_id: int, request: TopicUpdate, db: Session = Depends(get_db)):
    """Update topic details"""
    try:
        teacher_service = TeacherCurriculumService(db)
        topic = teacher_service.update_topic(
            topic_id=topic_id,
            title=request.title,
            description=request.description,
            order_index=request.order_index,
            learning_objectives=request.learning_objectives,
            estimated_duration_minutes=request.estimated_duration_minutes
        )
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return {
            "id": topic.id,
            "title": topic.title,
            "description": topic.description,
            "message": "Topic updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/teacher/topics/{topic_id}")
async def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    """Delete topic and all related content"""
    try:
        teacher_service = TeacherCurriculumService(db)
        success = teacher_service.delete_topic(topic_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return {"message": "Topic deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting topic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/teacher/topics/reorder")
async def reorder_topics(request: ReorderRequest, db: Session = Depends(get_db)):
    """Reorder topics within a lecture"""
    try:
        teacher_service = TeacherCurriculumService(db)
        success = teacher_service.reorder_topics(request.items)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reorder topics")
        
        return {"message": "Topics reordered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# SUBTOPIC MANAGEMENT
@app.post("/teacher/subtopics")
async def create_subtopic(request: SubTopicCreate, db: Session = Depends(get_db)):
    """Create a new subtopic"""
    try:
        teacher_service = TeacherCurriculumService(db)
        subtopic = teacher_service.create_subtopic(
            topic_id=request.topic_id,
            title=request.title,
            content=request.content,
            order_index=request.order_index,
            examples=request.examples,
            exercises=request.exercises,
            introduction_prompt=request.introduction_prompt,
            explanation_prompt=request.explanation_prompt,
            assessment_prompt=request.assessment_prompt
        )
        
        if not subtopic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        return {
            "id": subtopic.id,
            "title": subtopic.title,
            "content": subtopic.content,
            "message": "Subtopic created successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subtopic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/teacher/subtopics/{subtopic_id}")
async def update_subtopic(subtopic_id: int, request: SubTopicUpdate, db: Session = Depends(get_db)):
    """Update subtopic details"""
    try:
        teacher_service = TeacherCurriculumService(db)
        subtopic = teacher_service.update_subtopic(
            subtopic_id=subtopic_id,
            title=request.title,
            content=request.content,
            order_index=request.order_index,
            examples=request.examples,
            exercises=request.exercises,
            introduction_prompt=request.introduction_prompt,
            explanation_prompt=request.explanation_prompt,
            assessment_prompt=request.assessment_prompt
        )
        
        if not subtopic:
            raise HTTPException(status_code=404, detail="Subtopic not found")
        
        return {
            "id": subtopic.id,
            "title": subtopic.title,
            "content": subtopic.content,
            "message": "Subtopic updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subtopic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/teacher/subtopics/{subtopic_id}")
async def delete_subtopic(subtopic_id: int, db: Session = Depends(get_db)):
    """Delete subtopic"""
    try:
        teacher_service = TeacherCurriculumService(db)
        success = teacher_service.delete_subtopic(subtopic_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Subtopic not found")
        
        return {"message": "Subtopic deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting subtopic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/teacher/subtopics/reorder")
async def reorder_subtopics(request: ReorderRequest, db: Session = Depends(get_db)):
    """Reorder subtopics within a topic"""
    try:
        teacher_service = TeacherCurriculumService(db)
        success = teacher_service.reorder_subtopics(request.items)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reorder subtopics")
        
        return {"message": "Subtopics reordered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reordering subtopics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Legacy P0 Endpoints (for backward compatibility)

@app.post("/chat", response_model=ChatResponse)
async def chat_with_tutor_legacy(request: ChatRequest, db: Session = Depends(get_db)):
    """Legacy chat endpoint - now uses curriculum-driven approach"""
    try:
        # Convert to new format
        ai_tutor = AITutorService(openai_client, db)
        
        # If first message, start learning session
        if not hasattr(chat_with_tutor_legacy, 'started_sessions'):
            chat_with_tutor_legacy.started_sessions = set()
        
        if request.student_id not in chat_with_tutor_legacy.started_sessions:
            # Start learning session
            result = ai_tutor.initiate_learning_session(request.student_id, request.language)
            chat_with_tutor_legacy.started_sessions.add(request.student_id)
            
            return ChatResponse(
                response=result["message"],
                topic=result.get("topic", request.topic),
                understanding_level=result.get("understanding_level")
            )
        else:
            # Process as student response
            result = ai_tutor.process_student_response(request.student_id, request.message, request.language)
            
            return ChatResponse(
                response=result["message"],
                topic=result.get("topic", request.topic),
                understanding_level=result.get("understanding_level")
            )
        
    except Exception as e:
        logger.error(f"Error in legacy chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/conversation/{student_id}")
async def get_conversation_history_legacy(student_id: str, db: Session = Depends(get_db)):
    """Legacy conversation history endpoint"""
    try:
        from database import ConversationLog
        
        messages = (
            db.query(ConversationLog)
            .filter(ConversationLog.student_id == student_id)
            .order_by(ConversationLog.message_index)
            .all()
        )
        
        conversation = [
            {
                "role": msg.role,
                "content": msg.content,
                "topic": msg.topic.title if msg.topic else None,
                "subtopic": msg.subtopic.title if msg.subtopic else None,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
        return {"conversation": conversation}
        
    except Exception as e:
        logger.error(f"Error fetching conversation for {student_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/conversation/{student_id}")
async def clear_conversation_history_legacy(student_id: str, db: Session = Depends(get_db)):
    """Legacy conversation clearing endpoint"""
    try:
        from database import ConversationLog, StudentProgress
        
        # Clear conversation log
        db.query(ConversationLog).filter(ConversationLog.student_id == student_id).delete()
        
        # Reset progress
        db.query(StudentProgress).filter(StudentProgress.student_id == student_id).delete()
        
        # Remove from started sessions
        if hasattr(chat_with_tutor_legacy, 'started_sessions'):
            chat_with_tutor_legacy.started_sessions.discard(student_id)
        
        db.commit()
        
        return {"message": "Conversation history and progress cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing conversation for {student_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("API_HOST", "localhost"), 
        port=int(os.getenv("API_PORT", "8000")), 
        reload=True
    ) 