import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import (
    Lecture, Topic, SubTopic, StudentProgress, 
    ConversationLog, ProgressStatus, UnderstandingLevel
)

class TeacherCurriculumService:
    """Service for teacher curriculum management"""
    
    def __init__(self, db: Session):
        self.db = db

    # LECTURE MANAGEMENT
    def create_lecture(self, title: str, description: str, order_index: int) -> Lecture:
        """Create a new lecture"""
        lecture = Lecture(
            title=title,
            description=description,
            order_index=order_index,
            is_active=True
        )
        self.db.add(lecture)
        self.db.commit()
        self.db.refresh(lecture)
        return lecture

    def get_all_lectures(self) -> List[Lecture]:
        """Get all lectures ordered by index"""
        return self.db.query(Lecture).order_by(Lecture.order_index).all()

    def get_lecture_by_id(self, lecture_id: int) -> Optional[Lecture]:
        """Get lecture by ID"""
        return self.db.query(Lecture).filter(Lecture.id == lecture_id).first()

    def update_lecture(self, lecture_id: int, title: str, description: str, 
                      order_index: int, is_active: bool) -> Optional[Lecture]:
        """Update lecture details"""
        lecture = self.get_lecture_by_id(lecture_id)
        if not lecture:
            return None
        
        lecture.title = title
        lecture.description = description
        lecture.order_index = order_index
        lecture.is_active = is_active
        
        self.db.commit()
        self.db.refresh(lecture)
        return lecture

    def delete_lecture(self, lecture_id: int) -> bool:
        """Delete lecture and all related content"""
        lecture = self.get_lecture_by_id(lecture_id)
        if not lecture:
            return False
        
        self.db.delete(lecture)
        self.db.commit()
        return True

    def reorder_lectures(self, lecture_orders: List[Dict[str, int]]) -> bool:
        """Reorder lectures based on new indices"""
        try:
            for item in lecture_orders:
                lecture = self.get_lecture_by_id(item['id'])
                if lecture:
                    lecture.order_index = item['order_index']
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    # TOPIC MANAGEMENT
    def create_topic(self, lecture_id: int, title: str, description: str, 
                    order_index: int, learning_objectives: List[str], 
                    estimated_duration_minutes: int = 30) -> Optional[Topic]:
        """Create a new topic"""
        lecture = self.get_lecture_by_id(lecture_id)
        if not lecture:
            return None
        
        topic = Topic(
            lecture_id=lecture_id,
            title=title,
            description=description,
            order_index=order_index,
            learning_objectives=json.dumps(learning_objectives),
            estimated_duration_minutes=estimated_duration_minutes
        )
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def get_topics_by_lecture(self, lecture_id: int) -> List[Topic]:
        """Get all topics for a lecture"""
        return (
            self.db.query(Topic)
            .filter(Topic.lecture_id == lecture_id)
            .order_by(Topic.order_index)
            .all()
        )

    def get_topic_by_id(self, topic_id: int) -> Optional[Topic]:
        """Get topic by ID"""
        return self.db.query(Topic).filter(Topic.id == topic_id).first()

    def update_topic(self, topic_id: int, title: str, description: str, 
                    order_index: int, learning_objectives: List[str], 
                    estimated_duration_minutes: int) -> Optional[Topic]:
        """Update topic details"""
        topic = self.get_topic_by_id(topic_id)
        if not topic:
            return None
        
        topic.title = title
        topic.description = description
        topic.order_index = order_index
        topic.learning_objectives = json.dumps(learning_objectives)
        topic.estimated_duration_minutes = estimated_duration_minutes
        
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def delete_topic(self, topic_id: int) -> bool:
        """Delete topic and all related content"""
        topic = self.get_topic_by_id(topic_id)
        if not topic:
            return False
        
        self.db.delete(topic)
        self.db.commit()
        return True

    def reorder_topics(self, topic_orders: List[Dict[str, int]]) -> bool:
        """Reorder topics within a lecture"""
        try:
            for item in topic_orders:
                topic = self.get_topic_by_id(item['id'])
                if topic:
                    topic.order_index = item['order_index']
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    # SUBTOPIC MANAGEMENT
    def create_subtopic(self, topic_id: int, title: str, content: str, 
                       order_index: int, examples: List[Dict], 
                       exercises: List[Dict] = None,
                       introduction_prompt: str = None,
                       explanation_prompt: str = None,
                       assessment_prompt: str = None) -> Optional[SubTopic]:
        """Create a new subtopic"""
        topic = self.get_topic_by_id(topic_id)
        if not topic:
            return None
        
        subtopic = SubTopic(
            topic_id=topic_id,
            title=title,
            content=content,
            order_index=order_index,
            examples=json.dumps(examples) if examples else None,
            exercises=json.dumps(exercises) if exercises else None,
            introduction_prompt=introduction_prompt,
            explanation_prompt=explanation_prompt,
            assessment_prompt=assessment_prompt
        )
        self.db.add(subtopic)
        self.db.commit()
        self.db.refresh(subtopic)
        return subtopic

    def get_subtopics_by_topic(self, topic_id: int) -> List[SubTopic]:
        """Get all subtopics for a topic"""
        return (
            self.db.query(SubTopic)
            .filter(SubTopic.topic_id == topic_id)
            .order_by(SubTopic.order_index)
            .all()
        )

    def get_subtopic_by_id(self, subtopic_id: int) -> Optional[SubTopic]:
        """Get subtopic by ID"""
        return self.db.query(SubTopic).filter(SubTopic.id == subtopic_id).first()

    def update_subtopic(self, subtopic_id: int, title: str, content: str, 
                       order_index: int, examples: List[Dict],
                       exercises: List[Dict] = None,
                       introduction_prompt: str = None,
                       explanation_prompt: str = None,
                       assessment_prompt: str = None) -> Optional[SubTopic]:
        """Update subtopic details"""
        subtopic = self.get_subtopic_by_id(subtopic_id)
        if not subtopic:
            return None
        
        subtopic.title = title
        subtopic.content = content
        subtopic.order_index = order_index
        subtopic.examples = json.dumps(examples) if examples else None
        subtopic.exercises = json.dumps(exercises) if exercises else None
        subtopic.introduction_prompt = introduction_prompt
        subtopic.explanation_prompt = explanation_prompt
        subtopic.assessment_prompt = assessment_prompt
        
        self.db.commit()
        self.db.refresh(subtopic)
        return subtopic

    def delete_subtopic(self, subtopic_id: int) -> bool:
        """Delete subtopic"""
        subtopic = self.get_subtopic_by_id(subtopic_id)
        if not subtopic:
            return False
        
        self.db.delete(subtopic)
        self.db.commit()
        return True

    def reorder_subtopics(self, subtopic_orders: List[Dict[str, int]]) -> bool:
        """Reorder subtopics within a topic"""
        try:
            for item in subtopic_orders:
                subtopic = self.get_subtopic_by_id(item['id'])
                if subtopic:
                    subtopic.order_index = item['order_index']
            
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    # CURRICULUM STRUCTURE & ANALYTICS
    def get_full_curriculum_structure(self) -> Dict[str, Any]:
        """Get complete curriculum structure for teacher dashboard"""
        lectures = self.get_all_lectures()
        
        result = []
        for lecture in lectures:
            topics = []
            for topic in self.get_topics_by_lecture(lecture.id):
                subtopics = []
                for subtopic in self.get_subtopics_by_topic(topic.id):
                    subtopics.append({
                        "id": subtopic.id,
                        "title": subtopic.title,
                        "content": subtopic.content,
                        "order_index": subtopic.order_index,
                        "examples": json.loads(subtopic.examples) if subtopic.examples else [],
                        "exercises": json.loads(subtopic.exercises) if subtopic.exercises else [],
                        "introduction_prompt": subtopic.introduction_prompt,
                        "explanation_prompt": subtopic.explanation_prompt,
                        "assessment_prompt": subtopic.assessment_prompt
                    })
                
                topics.append({
                    "id": topic.id,
                    "title": topic.title,
                    "description": topic.description,
                    "order_index": topic.order_index,
                    "learning_objectives": json.loads(topic.learning_objectives) if topic.learning_objectives else [],
                    "estimated_duration_minutes": topic.estimated_duration_minutes,
                    "subtopics": subtopics
                })
            
            result.append({
                "id": lecture.id,
                "title": lecture.title,
                "description": lecture.description,
                "order_index": lecture.order_index,
                "is_active": lecture.is_active,
                "topics": topics
            })
        
        return {"lectures": result}

    def get_curriculum_analytics(self) -> Dict[str, Any]:
        """Get analytics for curriculum usage"""
        total_lectures = self.db.query(Lecture).count()
        total_topics = self.db.query(Topic).count()
        total_subtopics = self.db.query(SubTopic).count()
        
        # Student engagement stats
        active_students = self.db.query(StudentProgress.student_id).distinct().count()
        total_conversations = self.db.query(ConversationLog).count()
        
        # Understanding level distribution
        understanding_stats = (
            self.db.query(
                StudentProgress.understanding_level,
                self.db.func.count(StudentProgress.id).label('count')
            )
            .filter(StudentProgress.understanding_level.isnot(None))
            .group_by(StudentProgress.understanding_level)
            .all()
        )
        
        # Progress completion stats
        completion_stats = (
            self.db.query(
                StudentProgress.status,
                self.db.func.count(StudentProgress.id).label('count')
            )
            .group_by(StudentProgress.status)
            .all()
        )
        
        return {
            "curriculum_stats": {
                "total_lectures": total_lectures,
                "total_topics": total_topics,
                "total_subtopics": total_subtopics
            },
            "engagement_stats": {
                "active_students": active_students,
                "total_conversations": total_conversations,
                "avg_conversations_per_student": total_conversations / max(active_students, 1)
            },
            "understanding_distribution": {
                stat.understanding_level.value: stat.count 
                for stat in understanding_stats
            },
            "completion_distribution": {
                stat.status.value: stat.count 
                for stat in completion_stats
            }
        }

    def duplicate_curriculum_structure(self, source_lecture_id: int, new_title: str) -> Optional[Lecture]:
        """Duplicate an entire lecture with all topics and subtopics"""
        source_lecture = self.get_lecture_by_id(source_lecture_id)
        if not source_lecture:
            return None
        
        try:
            # Create new lecture
            max_order = self.db.query(self.db.func.max(Lecture.order_index)).scalar() or 0
            new_lecture = Lecture(
                title=new_title,
                description=f"Copy of {source_lecture.description}",
                order_index=max_order + 1,
                is_active=True
            )
            self.db.add(new_lecture)
            self.db.flush()
            
            # Copy all topics
            for topic in self.get_topics_by_lecture(source_lecture_id):
                new_topic = Topic(
                    lecture_id=new_lecture.id,
                    title=topic.title,
                    description=topic.description,
                    order_index=topic.order_index,
                    learning_objectives=topic.learning_objectives,
                    estimated_duration_minutes=topic.estimated_duration_minutes
                )
                self.db.add(new_topic)
                self.db.flush()
                
                # Copy all subtopics
                for subtopic in self.get_subtopics_by_topic(topic.id):
                    new_subtopic = SubTopic(
                        topic_id=new_topic.id,
                        title=subtopic.title,
                        content=subtopic.content,
                        order_index=subtopic.order_index,
                        examples=subtopic.examples,
                        exercises=subtopic.exercises,
                        introduction_prompt=subtopic.introduction_prompt,
                        explanation_prompt=subtopic.explanation_prompt,
                        assessment_prompt=subtopic.assessment_prompt
                    )
                    self.db.add(new_subtopic)
            
            self.db.commit()
            self.db.refresh(new_lecture)
            return new_lecture
            
        except Exception:
            self.db.rollback()
            return None 