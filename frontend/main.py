import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', '8000')}"

# Page configuration
st.set_page_config(
    page_title="AI Tutor - Curriculum-Driven Learning",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    .tutor-message {
        background-color: #28a745;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 20%;
        text-align: left;
    }
    .curriculum-info {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .progress-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .understanding-red {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
    .understanding-yellow {
        background-color: #fff8e1;
        color: #f57f17;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #ffeb3b;
    }
    .understanding-green {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #4caf50;
    }
    .sidebar-info {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables for P1B."""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'student_id' not in st.session_state:
        st.session_state.student_id = "default_student"
    if 'language' not in st.session_state:
        st.session_state.language = "en"
    if 'learning_session_started' not in st.session_state:
        st.session_state.learning_session_started = False
    if 'current_curriculum' not in st.session_state:
        st.session_state.current_curriculum = {}
    if 'progress_info' not in st.session_state:
        st.session_state.progress_info = {}

def start_learning_session(student_id: str, language: str) -> Optional[Dict[str, Any]]:
    """Start a new curriculum-driven learning session."""
    try:
        payload = {
            "student_id": student_id,
            "language": language
        }
        
        response = requests.post(f"{API_BASE_URL}/learning/start", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend API. Make sure the FastAPI server is running on localhost:8000")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def send_student_response(student_id: str, message: str, language: str) -> Optional[Dict[str, Any]]:
    """Send student response to curriculum-driven backend."""
    try:
        payload = {
            "student_id": student_id,
            "message": message,
            "language": language
        }
        
        response = requests.post(f"{API_BASE_URL}/learning/respond", json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend API. Make sure the FastAPI server is running on localhost:8000")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def get_student_progress(student_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed student progress information."""
    try:
        response = requests.get(f"{API_BASE_URL}/student/{student_id}/progress")
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except Exception:
        return None

def clear_conversation_legacy(student_id: str):
    """Clear conversation history using legacy endpoint."""
    try:
        response = requests.delete(f"{API_BASE_URL}/conversation/{student_id}")
        if response.status_code == 200:
            st.session_state.conversation = []
            st.session_state.learning_session_started = False
            st.session_state.current_curriculum = {}
            st.session_state.progress_info = {}
            st.success("Learning session reset!")
        else:
            st.error("Failed to reset session")
    except Exception as e:
        st.error(f"Error resetting session: {str(e)}")

def display_curriculum_info(curriculum_data: Dict[str, Any]):
    """Display current curriculum information."""
    if not curriculum_data:
        return
    
    st.markdown('<div class="curriculum-info">', unsafe_allow_html=True)
    
    # Current learning path
    st.markdown("**📚 Current Learning Path:**")
    if curriculum_data.get('lecture'):
        st.markdown(f"📖 **Lecture:** {curriculum_data['lecture']}")
    if curriculum_data.get('topic'):
        st.markdown(f"📝 **Topic:** {curriculum_data['topic']}")
    if curriculum_data.get('subtopic'):
        st.markdown(f"🎯 **Focus:** {curriculum_data['subtopic']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_understanding_indicator(understanding_level: Optional[str]):
    """Display understanding level indicator."""
    if not understanding_level:
        return
    
    if understanding_level == "red":
        st.markdown('<div class="understanding-red">🔴 <strong>Needs more explanation</strong> - Let me help clarify this concept</div>', unsafe_allow_html=True)
    elif understanding_level == "yellow":
        st.markdown('<div class="understanding-yellow">🟡 <strong>Partially understood</strong> - You\'re getting there!</div>', unsafe_allow_html=True)
    elif understanding_level == "green":
        st.markdown('<div class="understanding-green">🟢 <strong>Well understood</strong> - Great job! Ready to move forward</div>', unsafe_allow_html=True)

def display_progress_summary(progress_data: Dict[str, Any]):
    """Display progress summary."""
    if not progress_data:
        return
    
    st.markdown('<div class="progress-card">', unsafe_allow_html=True)
    st.markdown("**📊 Learning Progress**")
    
    completed = progress_data.get("completed_topics", 0)
    total = progress_data.get("total_topics", 1)
    percentage = progress_data.get("completion_percentage", 0)
    
    # Progress bar
    progress_bar = st.progress(percentage / 100)
    st.markdown(f"**{completed}/{total} topics completed ({percentage}%)**")
    
    # Progress indicators
    if percentage < 25:
        st.markdown("🚀 Just getting started - keep going!")
    elif percentage < 50:
        st.markdown("💪 Making good progress!")
    elif percentage < 75:
        st.markdown("🔥 You're doing great!")
    else:
        st.markdown("🏆 Almost there - excellent work!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function for P1B."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🐍 AI Python Tutor - P1</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Curriculum-driven AI tutoring with structured learning paths</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Learning Configuration")
        
        # Student ID
        st.session_state.student_id = st.text_input(
            "Student ID", 
            value=st.session_state.student_id,
            help="Unique identifier for the student"
        )
        
        # Language selection
        languages = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "hi": "Hindi",
            "zh": "Chinese"
        }
        
        language_options = list(languages.values())
        selected_language = st.selectbox(
            "Language",
            language_options,
            index=language_options.index(languages[st.session_state.language]) if st.session_state.language in languages else 0
        )
        
        # Update language code
        st.session_state.language = [k for k, v in languages.items() if v == selected_language][0]
        
        # Start Learning Session Button
        if not st.session_state.learning_session_started:
            if st.button("🚀 Start Learning Session", type="primary"):
                with st.spinner("Starting your personalized learning session..."):
                    result = start_learning_session(st.session_state.student_id, st.session_state.language)
                    
                    if result:
                        st.session_state.learning_session_started = True
                        st.session_state.current_curriculum = {
                            'lecture': result.get('lecture'),
                            'topic': result.get('topic'),
                            'subtopic': result.get('subtopic')
                        }
                        st.session_state.progress_info = result.get('progress', {})
                        
                        # Add AI's initial message to conversation
                        st.session_state.conversation.append({
                            "role": "assistant",
                            "content": result["message"],
                            "type": result["type"]
                        })
                        
                        st.rerun()
        
        # Session info
        if st.session_state.learning_session_started:
            st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
            st.markdown("**Session Info:**")
            st.markdown(f"👤 Student: {st.session_state.student_id}")
            st.markdown(f"🌍 Language: {selected_language}")
            st.markdown(f"💬 Messages: {len(st.session_state.conversation)}")
            st.markdown(f"📚 Session: Active")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Reset session button
            if st.button("🗑️ Reset Learning Session", type="secondary"):
                clear_conversation_legacy(st.session_state.student_id)
                st.rerun()
        
        # API status check
        st.markdown("---")
        try:
            health_response = requests.get(f"{API_BASE_URL}/health")
            if health_response.status_code == 200:
                data = health_response.json()
                st.success(f"✅ Backend API Connected")
                st.caption(f"Service: {data.get('service', 'unknown')}")
                st.caption(f"Version: {data.get('version', 'unknown')}")
            else:
                st.error("❌ Backend API Error")
        except:
            st.error("❌ Backend API Offline")
    
    # Main content area
    if not st.session_state.learning_session_started:
        # Welcome screen
        st.info("👋 Welcome! Click 'Start Learning Session' in the sidebar to begin your curriculum-driven Python learning journey.")
        
        st.markdown("### 🎯 What's New in P1:")
        st.markdown("""
        - **🤖 AI-Driven Teaching**: Your tutor leads the conversation and guides your learning path
        - **📚 Structured Curriculum**: Follow a carefully designed sequence of topics and subtopics  
        - **📊 Progress Tracking**: Real-time tracking with Red/Yellow/Green understanding levels
        - **🎓 Personalized Learning**: Adapts to your understanding and pace
        - **💾 Persistent Progress**: Your learning journey is saved and continues where you left off
        """)
        
        return
    
    # Display curriculum information
    if st.session_state.current_curriculum:
        display_curriculum_info(st.session_state.current_curriculum)
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💭 Learning Conversation")
        
        # Chat history display
        chat_container = st.container()
        with chat_container:
            if st.session_state.conversation:
                for i, msg in enumerate(st.session_state.conversation):
                    if msg['role'] == 'user':
                        st.markdown(f'<div class="user-message">👤 You: {msg["content"]}</div>', unsafe_allow_html=True)
                        
                        # Show understanding level if detected
                        if msg.get('understanding_level'):
                            display_understanding_indicator(msg['understanding_level'])
                    else:
                        message_type = msg.get('type', 'response')
                        icon = "🎯" if message_type == "introduction" else "🤖"
                        st.markdown(f'<div class="tutor-message">{icon} Tutor: {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.info("Your learning conversation will appear here once you start.")
        
        # Message input (only if session started)
        if st.session_state.learning_session_started:
            user_input = st.text_area(
                "Your response:",
                placeholder="Type your response or question here...",
                height=100,
                key="message_input"
            )
            
            # Send button
            col_send, col_help = st.columns([1, 2])
            
            with col_send:
                if st.button("📤 Send Response", type="primary", disabled=not user_input.strip()):
                    if user_input.strip():
                        # Add user message to conversation
                        st.session_state.conversation.append({
                            "role": "user",
                            "content": user_input
                        })
                        
                        # Send to API and get response
                        with st.spinner("🤔 Tutor is analyzing your response..."):
                            api_response = send_student_response(
                                st.session_state.student_id,
                                user_input,
                                st.session_state.language
                            )
                        
                        if api_response:
                            # Update curriculum info
                            st.session_state.current_curriculum = {
                                'lecture': api_response.get('lecture'),
                                'topic': api_response.get('topic'),
                                'subtopic': api_response.get('subtopic')
                            }
                            st.session_state.progress_info = api_response.get('progress', {})
                            
                            # Add understanding level to user message
                            if api_response.get('understanding_level'):
                                st.session_state.conversation[-1]['understanding_level'] = api_response['understanding_level']
                            
                            # Add tutor response to conversation
                            st.session_state.conversation.append({
                                "role": "assistant",
                                "content": api_response["message"],
                                "type": api_response["type"]
                            })
                            
                            # Show next action if available
                            if api_response.get("next_action") == "ready_for_next":
                                st.success("🎉 Great! You've mastered this concept. The tutor will guide you to the next topic.")
                        
                        # Clear input and rerun
                        st.rerun()
            
            with col_help:
                st.markdown("**💡 Tips:**")
                st.caption("• Be honest about your understanding")
                st.caption("• Ask for clarification if confused")
                st.caption("• The AI tutor will guide your learning path")
    
    with col2:
        st.subheader("📊 Your Progress")
        
        # Progress summary
        if st.session_state.progress_info:
            display_progress_summary(st.session_state.progress_info)
        
        # Learning tips specific to curriculum-driven approach
        st.markdown("---")
        st.subheader("🎓 Learning Guide")
        tips = [
            "Let the AI tutor guide your learning path",
            "Be honest about your understanding level",
            "Ask questions when concepts are unclear",
            "Practice with the examples provided",
            "Take your time - quality over speed"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")
        
        # Understanding levels guide
        st.markdown("---")
        st.subheader("🎯 Understanding Levels")
        st.markdown('<div class="understanding-green">🟢 <strong>Green:</strong> I understand clearly</div>', unsafe_allow_html=True)
        st.markdown('<div class="understanding-yellow">🟡 <strong>Yellow:</strong> I partially understand</div>', unsafe_allow_html=True)
        st.markdown('<div class="understanding-red">🔴 <strong>Red:</strong> I need more help</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 