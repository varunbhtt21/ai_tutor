import streamlit as st
import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', '8000')}"

# Page configuration
st.set_page_config(
    page_title="AI Tutor - Python Learning Assistant",
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
    .sidebar-info {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    if 'student_id' not in st.session_state:
        st.session_state.student_id = "default_student"
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = "Python Basics"
    if 'language' not in st.session_state:
        st.session_state.language = "en"

def send_message_to_api(message: str, student_id: str, topic: str, language: str):
    """Send message to the FastAPI backend."""
    try:
        payload = {
            "message": message,
            "student_id": student_id,
            "topic": topic,
            "language": language
        }
        
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        
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

def clear_conversation():
    """Clear the conversation history."""
    try:
        response = requests.delete(f"{API_BASE_URL}/conversation/{st.session_state.student_id}")
        if response.status_code == 200:
            st.session_state.conversation = []
            st.success("Conversation cleared!")
        else:
            st.error("Failed to clear conversation")
    except Exception as e:
        st.error(f"Error clearing conversation: {str(e)}")

def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🐍 AI Python Tutor</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Your personal AI assistant for learning Python programming</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Student ID
        st.session_state.student_id = st.text_input(
            "Student ID", 
            value=st.session_state.student_id,
            help="Unique identifier for the student"
        )
        
        # Topic selection
        topics = [
            "Python Basics",
            "Variables and Data Types", 
            "Control Structures",
            "Functions",
            "Lists and Dictionaries",
            "Object-Oriented Programming",
            "File Handling",
            "Error Handling"
        ]
        
        st.session_state.current_topic = st.selectbox(
            "Current Topic",
            topics,
            index=topics.index(st.session_state.current_topic) if st.session_state.current_topic in topics else 0
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
        
        # Session info
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.markdown("**Session Info:**")
        st.markdown(f"👤 Student: {st.session_state.student_id}")
        st.markdown(f"📚 Topic: {st.session_state.current_topic}")
        st.markdown(f"🌍 Language: {selected_language}")
        st.markdown(f"💬 Messages: {len(st.session_state.conversation)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", type="secondary"):
            clear_conversation()
            st.rerun()
        
        # API status check
        st.markdown("---")
        try:
            health_response = requests.get(f"{API_BASE_URL}/health")
            if health_response.status_code == 200:
                st.success("✅ Backend API Connected")
            else:
                st.error("❌ Backend API Error")
        except:
            st.error("❌ Backend API Offline")
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💭 Chat with your AI Tutor")
        
        # Chat history display
        chat_container = st.container()
        with chat_container:
            if st.session_state.conversation:
                for i, msg in enumerate(st.session_state.conversation):
                    if msg['role'] == 'user':
                        st.markdown(f'<div class="user-message">👤 You: {msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="tutor-message">🤖 Tutor: {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.info("👋 Welcome! Start a conversation with your AI tutor by typing a message below.")
        
        # Message input
        user_input = st.text_area(
            "Type your message here:",
            placeholder=f"Ask me anything about {st.session_state.current_topic}...",
            height=100,
            key="message_input"
        )
        
        # Send button
        col_send, col_example = st.columns([1, 2])
        
        with col_send:
            if st.button("📤 Send Message", type="primary", disabled=not user_input.strip()):
                if user_input.strip():
                    # Add user message to conversation
                    st.session_state.conversation.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    # Send to API and get response
                    with st.spinner("🤔 Tutor is thinking..."):
                        api_response = send_message_to_api(
                            user_input,
                            st.session_state.student_id,
                            st.session_state.current_topic,
                            st.session_state.language
                        )
                    
                    if api_response:
                        # Add tutor response to conversation
                        st.session_state.conversation.append({
                            "role": "assistant",
                            "content": api_response["response"]
                        })
                        
                        # Show understanding level if detected
                        if api_response.get("understanding_level"):
                            if api_response["understanding_level"] == "needs_help":
                                st.warning("🤔 It seems you might need more explanation. Feel free to ask for clarification!")
                            elif api_response["understanding_level"] == "understood":
                                st.success("🎉 Great! You seem to understand this concept well!")
                    
                    # Clear input and rerun
                    st.rerun()
        
        with col_example:
            if st.button("💡 Give me example questions"):
                example_questions = [
                    "What are variables in Python?",
                    "How do I create a list?",
                    "What's the difference between a list and a tuple?",
                    "Can you explain loops with examples?",
                    "I don't understand functions, can you help?"
                ]
                st.info("**Example questions you can ask:**\n" + "\n".join([f"• {q}" for q in example_questions]))
    
    with col2:
        st.subheader("📊 Learning Progress")
        
        # Simple progress tracking for P0
        total_messages = len(st.session_state.conversation)
        user_messages = len([msg for msg in st.session_state.conversation if msg['role'] == 'user'])
        
        if total_messages > 0:
            st.metric("Total Messages", total_messages)
            st.metric("Your Questions", user_messages)
            
            # Simple engagement metric
            if user_messages > 5:
                st.success("🔥 Highly Engaged!")
            elif user_messages > 2:
                st.info("👍 Good Engagement")
            else:
                st.warning("💪 Keep asking questions!")
        else:
            st.info("Start chatting to see your progress!")
        
        # Quick tips
        st.markdown("---")
        st.subheader("💡 Quick Tips")
        tips = [
            "Ask specific questions for better answers",
            "Rate your understanding on a scale of 1-3",
            "Request examples for complex concepts",
            "Don't hesitate to say 'I don't understand'"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")

if __name__ == "__main__":
    main() 