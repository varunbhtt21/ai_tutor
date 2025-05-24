import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import enum
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_tutor.db")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Enums for status tracking
class ProgressStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class UnderstandingLevel(enum.Enum):
    RED = "red"          # Not understood
    YELLOW = "yellow"    # Partially understood  
    GREEN = "green"      # Well understood

# Database Models
class Student(Base):
    __tablename__ = "students"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    preferred_language = Column(String, default="en")
    current_lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    current_lecture = relationship("Lecture", back_populates="current_students")
    progress_records = relationship("StudentProgress", back_populates="student")
    conversations = relationship("ConversationLog", back_populates="student")
    notes = relationship("StudentNote", back_populates="student")

class Lecture(Base):
    __tablename__ = "lectures"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    topics = relationship("Topic", back_populates="lecture", cascade="all, delete-orphan")
    current_students = relationship("Student", back_populates="current_lecture")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    learning_objectives = Column(Text)  # JSON string of objectives
    estimated_duration_minutes = Column(Integer, default=30)
    
    # Relationships
    lecture = relationship("Lecture", back_populates="topics")
    subtopics = relationship("SubTopic", back_populates="topic", cascade="all, delete-orphan")
    progress_records = relationship("StudentProgress", back_populates="topic")

class SubTopic(Base):
    __tablename__ = "subtopics"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Main teaching content
    examples = Column(Text)  # JSON string of code examples
    exercises = Column(Text)  # JSON string of practice exercises
    order_index = Column(Integer, nullable=False)
    
    # AI Teaching prompts
    introduction_prompt = Column(Text)  # How AI should introduce this subtopic
    explanation_prompt = Column(Text)   # How AI should explain concepts
    assessment_prompt = Column(Text)    # How AI should check understanding
    
    # Relationships
    topic = relationship("Topic", back_populates="subtopics")
    progress_records = relationship("StudentProgress", back_populates="subtopic")

class StudentProgress(Base):
    __tablename__ = "student_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=True)
    
    # Progress tracking
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED)
    understanding_level = Column(Enum(UnderstandingLevel), nullable=True)
    completion_percentage = Column(Integer, default=0)  # 0-100
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # AI assessment
    ai_assessment_notes = Column(Text)  # AI's notes on student progress
    time_spent_minutes = Column(Integer, default=0)
    
    # Relationships
    student = relationship("Student", back_populates="progress_records")
    topic = relationship("Topic", back_populates="progress_records")
    subtopic = relationship("SubTopic", back_populates="progress_records")

class ConversationLog(Base):
    __tablename__ = "conversation_log"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=True)
    
    # Message content
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    language = Column(String, default="en")
    
    # Context
    session_id = Column(String, nullable=True)
    message_index = Column(Integer, nullable=False)  # Order in conversation
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tokens_used = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="conversations")

class StudentNote(Base):
    __tablename__ = "student_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    subtopic_id = Column(Integer, ForeignKey("subtopics.id"), nullable=True)
    
    # Note content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Markdown formatted notes
    summary = Column(Text)  # Brief summary
    key_concepts = Column(Text)  # JSON array of key concepts learned
    code_examples = Column(Text)  # JSON array of code examples
    
    # Auto-generation metadata
    generated_from_conversation = Column(Boolean, default=True)
    conversation_start_id = Column(Integer, nullable=True)
    conversation_end_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="notes")

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine) 