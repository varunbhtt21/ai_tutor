import json
import re
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from openai import OpenAI
import os

from database import (
    Student, Lecture, Topic, SubTopic, StudentProgress, 
    ConversationLog, StudentNote, ProgressStatus, UnderstandingLevel
)

class AITutorService:
    def __init__(self, openai_client: OpenAI, db: Session):
        self.openai_client = openai_client
        self.db = db
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    def get_or_create_student(self, student_id: str, name: str = None, language: str = "en") -> Student:
        """Get existing student or create new one"""
        student = self.db.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            # Create new student and assign first lecture
            first_lecture = self.db.query(Lecture).order_by(Lecture.order_index).first()
            student = Student(
                id=student_id,
                name=name,
                preferred_language=language,
                current_lecture_id=first_lecture.id if first_lecture else None
            )
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
        
        return student

    def get_current_learning_context(self, student: Student) -> Dict[str, Any]:
        """Get student's current position in curriculum"""
        if not student.current_lecture_id:
            return {"status": "no_lecture_assigned"}
        
        # Get current lecture
        lecture = self.db.query(Lecture).filter(Lecture.id == student.current_lecture_id).first()
        
        # Find student's current progress
        progress = (
            self.db.query(StudentProgress)
            .filter(StudentProgress.student_id == student.id)
            .filter(StudentProgress.status != ProgressStatus.COMPLETED)
            .join(Topic)
            .filter(Topic.lecture_id == lecture.id)
            .order_by(Topic.order_index, SubTopic.order_index)
            .first()
        )
        
        if not progress:
            # Start with first topic of current lecture
            first_topic = (
                self.db.query(Topic)
                .filter(Topic.lecture_id == lecture.id)
                .order_by(Topic.order_index)
                .first()
            )
            
            if first_topic:
                first_subtopic = (
                    self.db.query(SubTopic)
                    .filter(SubTopic.topic_id == first_topic.id)
                    .order_by(SubTopic.order_index)
                    .first()
                )
                
                # Create progress record
                progress = StudentProgress(
                    student_id=student.id,
                    topic_id=first_topic.id,
                    subtopic_id=first_subtopic.id if first_subtopic else None,
                    status=ProgressStatus.IN_PROGRESS
                )
                self.db.add(progress)
                self.db.commit()
                self.db.refresh(progress)
        
        return {
            "lecture": lecture,
            "topic": progress.topic if progress else None,
            "subtopic": progress.subtopic if progress and progress.subtopic else None,
            "progress": progress
        }

    def initiate_learning_session(self, student_id: str, language: str = "en") -> Dict[str, Any]:
        """Start or continue a learning session with AI-driven curriculum"""
        student = self.get_or_create_student(student_id, language=language)
        context = self.get_current_learning_context(student)
        
        if context["status"] == "no_lecture_assigned":
            return {
                "type": "error",
                "message": "No curriculum available. Please contact your instructor."
            }
        
        subtopic = context["subtopic"]
        topic = context["topic"]
        
        if not subtopic:
            return {
                "type": "error", 
                "message": "No subtopic found. Curriculum may be incomplete."
            }
        
        # Check if this is the start of a new subtopic
        conversation_count = (
            self.db.query(ConversationLog)
            .filter(ConversationLog.student_id == student_id)
            .filter(ConversationLog.subtopic_id == subtopic.id)
            .count()
        )
        
        if conversation_count == 0:
            # First time on this subtopic - use introduction prompt
            ai_message = self._generate_introduction(subtopic, topic, language)
            message_type = "introduction"
        else:
            # Continue existing subtopic
            ai_message = self._generate_continuation(subtopic, topic, student_id, language)
            message_type = "continuation"
        
        # Save AI message to conversation log
        self._save_conversation_message(
            student_id=student_id,
            role="assistant",
            content=ai_message,
            topic_id=topic.id,
            subtopic_id=subtopic.id,
            language=language
        )
        
        return {
            "type": message_type,
            "message": ai_message,
            "topic": topic.title,
            "subtopic": subtopic.title,
            "lecture": context["lecture"].title,
            "progress": self._get_progress_summary(student)
        }

    def process_student_response(self, student_id: str, message: str, language: str = "en") -> Dict[str, Any]:
        """Process student's response and provide AI tutor feedback"""
        student = self.get_or_create_student(student_id, language=language)
        context = self.get_current_learning_context(student)
        
        subtopic = context["subtopic"]
        topic = context["topic"]
        progress = context["progress"]
        
        # Save student message
        self._save_conversation_message(
            student_id=student_id,
            role="user", 
            content=message,
            topic_id=topic.id,
            subtopic_id=subtopic.id,
            language=language
        )
        
        # Analyze student understanding
        understanding = self._analyze_understanding(message)
        
        # Update progress if understanding detected
        if understanding and progress:
            progress.understanding_level = understanding
            self.db.commit()
        
        # Generate AI response based on understanding and curriculum
        ai_response = self._generate_curriculum_response(
            subtopic, topic, student_id, message, understanding, language
        )
        
        # Save AI response
        self._save_conversation_message(
            student_id=student_id,
            role="assistant",
            content=ai_response,
            topic_id=topic.id,
            subtopic_id=subtopic.id,
            language=language
        )
        
        # Check if subtopic is completed
        next_action = self._check_subtopic_completion(student_id, subtopic, understanding)
        
        return {
            "type": "response",
            "message": ai_response,
            "understanding_level": understanding.value if understanding else None,
            "next_action": next_action,
            "progress": self._get_progress_summary(student)
        }

    def _generate_introduction(self, subtopic: SubTopic, topic: Topic, language: str) -> str:
        """Generate introduction message for a new subtopic"""
        examples_text = ""
        if subtopic.examples:
            examples = json.loads(subtopic.examples)
            examples_text = "\n\nHere are some examples:\n" + "\n".join([
                f"• {ex.get('code', ex.get('example', ''))}: {ex.get('explanation', '')}"
                for ex in examples[:2]  # Limit to 2 examples
            ])
        
        system_prompt = f"""You are an expert Python tutor. You're starting a new lesson on "{subtopic.title}" 
within the topic "{topic.title}".

Content: {subtopic.content}
{examples_text}

Use this introduction prompt as guidance: {subtopic.introduction_prompt}

Adapt your response to {language} language if not English. Be encouraging, clear, and engaging.
End with a question to check their initial understanding or get them engaged."""
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content

    def _generate_continuation(self, subtopic: SubTopic, topic: Topic, student_id: str, language: str) -> str:
        """Generate continuation message for ongoing subtopic"""
        # Get recent conversation
        recent_messages = (
            self.db.query(ConversationLog)
            .filter(ConversationLog.student_id == student_id)
            .filter(ConversationLog.subtopic_id == subtopic.id)
            .order_by(ConversationLog.created_at.desc())
            .limit(6)
            .all()
        )
        
        conversation_context = "\n".join([
            f"{msg.role}: {msg.content}" for msg in reversed(recent_messages)
        ])
        
        system_prompt = f"""Continue teaching "{subtopic.title}" within "{topic.title}".

Previous conversation:
{conversation_context}

Content focus: {subtopic.content}
Explanation guidance: {subtopic.explanation_prompt}

Continue the learning conversation naturally. Adapt to {language} if not English.
Ask a follow-up question or suggest the next learning step."""
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content

    def _generate_curriculum_response(self, subtopic: SubTopic, topic: Topic, student_id: str, 
                                    student_message: str, understanding: Optional[UnderstandingLevel], 
                                    language: str) -> str:
        """Generate AI response based on curriculum and student understanding"""
        
        # Get conversation context
        recent_messages = (
            self.db.query(ConversationLog)
            .filter(ConversationLog.student_id == student_id)
            .filter(ConversationLog.subtopic_id == subtopic.id)
            .order_by(ConversationLog.created_at.desc())
            .limit(8)
            .all()
        )
        
        conversation_context = "\n".join([
            f"{msg.role}: {msg.content}" for msg in reversed(recent_messages[:-1])  # Exclude current message
        ])
        
        understanding_guidance = ""
        if understanding == UnderstandingLevel.RED:
            understanding_guidance = "Student seems confused. Provide simpler explanation with more examples."
        elif understanding == UnderstandingLevel.YELLOW:
            understanding_guidance = "Student partially understands. Clarify specific points and provide additional examples."
        elif understanding == UnderstandingLevel.GREEN:
            understanding_guidance = "Student understands well. Consider moving to next concept or providing advanced examples."
        
        examples_text = ""
        if subtopic.examples:
            examples = json.loads(subtopic.examples)
            examples_text = "\n\nAvailable examples:\n" + "\n".join([
                f"• {ex.get('code', ex.get('example', ''))}: {ex.get('explanation', '')}"
                for ex in examples
            ])
        
        system_prompt = f"""You are teaching "{subtopic.title}" within "{topic.title}".

Content: {subtopic.content}
{examples_text}

Previous conversation:
{conversation_context}

Student just said: "{student_message}"

{understanding_guidance}

Teaching guidance: {subtopic.explanation_prompt}
Assessment guidance: {subtopic.assessment_prompt}

Respond naturally in {language}. Provide helpful feedback, examples, or questions as appropriate.
Guide the student progressively through the learning material."""
        
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content

    def _analyze_understanding(self, message: str) -> Optional[UnderstandingLevel]:
        """Analyze student message to determine understanding level"""
        message_lower = message.lower()
        
        # Red indicators (confusion/difficulty)
        red_indicators = [
            "don't understand", "confused", "unclear", "don't get it", 
            "what does", "i'm lost", "makes no sense", "too hard",
            "can you explain", "what is", "help me understand"
        ]
        
        # Green indicators (understanding/confidence)
        green_indicators = [
            "i understand", "got it", "makes sense", "i see", "clear now",
            "understand now", "that's easy", "i know", "simple"
        ]
        
        # Yellow indicators (partial understanding)
        yellow_indicators = [
            "think i understand", "sort of", "kind of", "partially",
            "mostly clear", "almost", "not completely sure"
        ]
        
        for indicator in red_indicators:
            if indicator in message_lower:
                return UnderstandingLevel.RED
                
        for indicator in green_indicators:
            if indicator in message_lower:
                return UnderstandingLevel.GREEN
                
        for indicator in yellow_indicators:
            if indicator in message_lower:
                return UnderstandingLevel.YELLOW
        
        return None

    def _save_conversation_message(self, student_id: str, role: str, content: str, 
                                 topic_id: int, subtopic_id: int, language: str):
        """Save message to conversation log"""
        # Get next message index
        last_message = (
            self.db.query(ConversationLog)
            .filter(ConversationLog.student_id == student_id)
            .order_by(ConversationLog.message_index.desc())
            .first()
        )
        
        next_index = (last_message.message_index + 1) if last_message else 1
        
        message = ConversationLog(
            student_id=student_id,
            topic_id=topic_id,
            subtopic_id=subtopic_id,
            role=role,
            content=content,
            language=language,
            message_index=next_index
        )
        
        self.db.add(message)
        self.db.commit()

    def _check_subtopic_completion(self, student_id: str, subtopic: SubTopic, 
                                 understanding: Optional[UnderstandingLevel]) -> str:
        """Check if subtopic should be marked as completed"""
        if understanding == UnderstandingLevel.GREEN:
            # Check if student has had enough interaction with this subtopic
            message_count = (
                self.db.query(ConversationLog)
                .filter(ConversationLog.student_id == student_id)
                .filter(ConversationLog.subtopic_id == subtopic.id)
                .count()
            )
            
            if message_count >= 4:  # At least 2 exchanges
                return "ready_for_next"
        
        return "continue_current"

    def _get_progress_summary(self, student: Student) -> Dict[str, Any]:
        """Get student's overall progress summary"""
        total_topics = (
            self.db.query(Topic)
            .filter(Topic.lecture_id == student.current_lecture_id)
            .count()
        )
        
        completed_topics = (
            self.db.query(StudentProgress)
            .filter(StudentProgress.student_id == student.id)
            .filter(StudentProgress.status == ProgressStatus.COMPLETED)
            .count()
        )
        
        return {
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "completion_percentage": int((completed_topics / total_topics) * 100) if total_topics > 0 else 0
        } 