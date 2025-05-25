import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
import pandas as pd

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', '8000')}"

# Page configuration
st.set_page_config(
    page_title="AI Tutor - Teacher Dashboard",
    page_icon="👩‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for teacher dashboard
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4e79;
        margin-bottom: 2rem;
    }
    .dashboard-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .lecture-card {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
    }
    .topic-card {
        background-color: #f3e5f5;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #9c27b0;
        margin: 0.3rem 0 0.3rem 1rem;
    }
    .subtopic-card {
        background-color: #e8f5e8;
        padding: 0.6rem;
        border-radius: 4px;
        border-left: 2px solid #4caf50;
        margin: 0.2rem 0 0.2rem 2rem;
    }
    .action-button {
        margin: 0.2rem;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        border: none;
        cursor: pointer;
    }
    .edit-button {
        background-color: #ffc107;
        color: #212529;
    }
    .delete-button {
        background-color: #dc3545;
        color: white;
    }
    .add-button {
        background-color: #28a745;
        color: white;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state for teacher dashboard"""
    if 'curriculum_data' not in st.session_state:
        st.session_state.curriculum_data = None
    if 'analytics_data' not in st.session_state:
        st.session_state.analytics_data = None
    if 'selected_lecture' not in st.session_state:
        st.session_state.selected_lecture = None
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = None
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = None

def fetch_curriculum_data():
    """Fetch curriculum structure from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/teacher/curriculum")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch curriculum: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching curriculum: {str(e)}")
        return None

def fetch_analytics_data():
    """Fetch analytics data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/teacher/analytics")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch analytics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching analytics: {str(e)}")
        return None

def create_lecture(title: str, description: str, order_index: int):
    """Create a new lecture"""
    try:
        payload = {
            "title": title,
            "description": description,
            "order_index": order_index
        }
        response = requests.post(f"{API_BASE_URL}/teacher/lectures", json=payload)
        if response.status_code == 200:
            st.success("Lecture created successfully!")
            return True
        else:
            st.error(f"Failed to create lecture: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error creating lecture: {str(e)}")
        return False

def create_topic(lecture_id: int, title: str, description: str, order_index: int, 
                learning_objectives: List[str], duration: int):
    """Create a new topic"""
    try:
        payload = {
            "lecture_id": lecture_id,
            "title": title,
            "description": description,
            "order_index": order_index,
            "learning_objectives": learning_objectives,
            "estimated_duration_minutes": duration
        }
        response = requests.post(f"{API_BASE_URL}/teacher/topics", json=payload)
        if response.status_code == 200:
            st.success("Topic created successfully!")
            return True
        else:
            st.error(f"Failed to create topic: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error creating topic: {str(e)}")
        return False

def create_subtopic(topic_id: int, title: str, content: str, order_index: int,
                   examples: List[dict], introduction_prompt: str, 
                   explanation_prompt: str, assessment_prompt: str):
    """Create a new subtopic"""
    try:
        payload = {
            "topic_id": topic_id,
            "title": title,
            "content": content,
            "order_index": order_index,
            "examples": examples,
            "introduction_prompt": introduction_prompt,
            "explanation_prompt": explanation_prompt,
            "assessment_prompt": assessment_prompt
        }
        response = requests.post(f"{API_BASE_URL}/teacher/subtopics", json=payload)
        if response.status_code == 200:
            st.success("Subtopic created successfully!")
            return True
        else:
            st.error(f"Failed to create subtopic: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error creating subtopic: {str(e)}")
        return False

def display_analytics_dashboard():
    """Display analytics dashboard"""
    st.subheader("📊 Curriculum Analytics")
    
    analytics = fetch_analytics_data()
    if not analytics:
        st.error("Failed to load analytics data")
        return
    
    # Curriculum stats
    curriculum_stats = analytics.get("curriculum_stats", {})
    engagement_stats = analytics.get("engagement_stats", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Lectures", curriculum_stats.get("total_lectures", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Topics", curriculum_stats.get("total_topics", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Subtopics", curriculum_stats.get("total_subtopics", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Students", engagement_stats.get("active_students", 0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Understanding distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Understanding Levels")
        understanding_dist = analytics.get("understanding_distribution", {})
        if understanding_dist:
            df_understanding = pd.DataFrame(list(understanding_dist.items()), 
                                          columns=['Level', 'Count'])
            st.bar_chart(df_understanding.set_index('Level'))
        else:
            st.info("No understanding data available yet")
    
    with col2:
        st.subheader("Progress Status")
        completion_dist = analytics.get("completion_distribution", {})
        if completion_dist:
            df_completion = pd.DataFrame(list(completion_dist.items()), 
                                       columns=['Status', 'Count'])
            st.bar_chart(df_completion.set_index('Status'))
        else:
            st.info("No progress data available yet")

def display_curriculum_builder():
    """Display curriculum builder interface"""
    st.subheader("🏗️ Curriculum Builder")
    
    # Fetch current curriculum
    curriculum = fetch_curriculum_data()
    if not curriculum:
        st.error("Failed to load curriculum data")
        return
    
    lectures = curriculum.get("lectures", [])
    
    # Add new lecture section
    with st.expander("➕ Add New Lecture"):
        with st.form("new_lecture_form"):
            title = st.text_input("Lecture Title")
            description = st.text_area("Description")
            order_index = st.number_input("Order Index", min_value=1, value=len(lectures) + 1)
            
            if st.form_submit_button("Create Lecture"):
                if title and description:
                    if create_lecture(title, description, order_index):
                        st.rerun()
                else:
                    st.error("Please fill in all fields")
    
    # Display existing lectures
    for lecture in lectures:
        st.markdown('<div class="lecture-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**📚 {lecture['title']}**")
            st.markdown(f"*{lecture['description']}*")
            st.caption(f"Order: {lecture['order_index']} | Active: {lecture['is_active']}")
        
        with col2:
            if st.button(f"➕ Add Topic", key=f"add_topic_{lecture['id']}"):
                st.session_state.selected_lecture = lecture['id']
        
        # Display topics
        for topic in lecture.get('topics', []):
            st.markdown('<div class="topic-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**📝 {topic['title']}**")
                st.markdown(f"*{topic['description']}*")
                st.caption(f"Duration: {topic['estimated_duration_minutes']} min")
                
                # Show learning objectives
                if topic.get('learning_objectives'):
                    st.markdown("**Objectives:**")
                    for obj in topic['learning_objectives']:
                        st.markdown(f"• {obj}")
            
            with col2:
                if st.button(f"➕ Add Subtopic", key=f"add_subtopic_{topic['id']}"):
                    st.session_state.selected_topic = topic['id']
            
            # Display subtopics
            for subtopic in topic.get('subtopics', []):
                st.markdown('<div class="subtopic-card">', unsafe_allow_html=True)
                st.markdown(f"**🎯 {subtopic['title']}**")
                
                with st.expander(f"View Details - {subtopic['title']}"):
                    st.markdown("**Content:**")
                    st.markdown(subtopic['content'])
                    
                    if subtopic.get('examples'):
                        st.markdown("**Examples:**")
                        for example in subtopic['examples']:
                            st.code(example.get('code', ''), language='python')
                            st.caption(example.get('explanation', ''))
                    
                    st.markdown("**AI Prompts:**")
                    st.markdown(f"*Introduction:* {subtopic.get('introduction_prompt', 'Not set')}")
                    st.markdown(f"*Explanation:* {subtopic.get('explanation_prompt', 'Not set')}")
                    st.markdown(f"*Assessment:* {subtopic.get('assessment_prompt', 'Not set')}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

def display_topic_form():
    """Display form for adding new topic"""
    if st.session_state.selected_lecture:
        st.subheader(f"➕ Add Topic to Lecture {st.session_state.selected_lecture}")
        
        with st.form("new_topic_form"):
            title = st.text_input("Topic Title")
            description = st.text_area("Description")
            order_index = st.number_input("Order Index", min_value=1, value=1)
            duration = st.number_input("Estimated Duration (minutes)", min_value=5, value=30)
            
            # Learning objectives
            st.markdown("**Learning Objectives:**")
            objectives = []
            for i in range(3):
                obj = st.text_input(f"Objective {i+1}", key=f"obj_{i}")
                if obj:
                    objectives.append(obj)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Create Topic"):
                    if title and description and objectives:
                        if create_topic(st.session_state.selected_lecture, title, description, 
                                      order_index, objectives, duration):
                            st.session_state.selected_lecture = None
                            st.rerun()
                    else:
                        st.error("Please fill in all required fields")
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.selected_lecture = None
                    st.rerun()

def display_subtopic_form():
    """Display form for adding new subtopic"""
    if st.session_state.selected_topic:
        st.subheader(f"➕ Add Subtopic to Topic {st.session_state.selected_topic}")
        
        with st.form("new_subtopic_form"):
            title = st.text_input("Subtopic Title")
            content = st.text_area("Content", height=150)
            order_index = st.number_input("Order Index", min_value=1, value=1)
            
            # Examples
            st.markdown("**Code Examples:**")
            examples = []
            for i in range(2):
                st.markdown(f"*Example {i+1}:*")
                code = st.text_area(f"Code", key=f"code_{i}", height=80)
                explanation = st.text_input(f"Explanation", key=f"exp_{i}")
                if code and explanation:
                    examples.append({"code": code, "explanation": explanation})
            
            # AI Prompts
            st.markdown("**AI Teaching Prompts:**")
            intro_prompt = st.text_area("Introduction Prompt", 
                                       placeholder="How should AI introduce this concept?")
            explain_prompt = st.text_area("Explanation Prompt", 
                                        placeholder="How should AI explain this concept?")
            assess_prompt = st.text_area("Assessment Prompt", 
                                       placeholder="How should AI check understanding?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Create Subtopic"):
                    if title and content:
                        if create_subtopic(st.session_state.selected_topic, title, content, 
                                         order_index, examples, intro_prompt, 
                                         explain_prompt, assess_prompt):
                            st.session_state.selected_topic = None
                            st.rerun()
                    else:
                        st.error("Please fill in title and content")
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.selected_topic = None
                    st.rerun()

def main():
    """Main teacher dashboard application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">👩‍🏫 AI Tutor - Teacher Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Design and manage your AI-driven curriculum</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🎛️ Dashboard Navigation")
        
        page = st.selectbox(
            "Select Page",
            ["📊 Analytics", "🏗️ Curriculum Builder", "🧪 Preview & Test", "⚙️ Settings"]
        )
        
        # API status
        st.markdown("---")
        try:
            health_response = requests.get(f"{API_BASE_URL}/health")
            if health_response.status_code == 200:
                data = health_response.json()
                st.success("✅ Backend Connected")
                st.caption(f"Version: {data.get('version', 'unknown')}")
            else:
                st.error("❌ Backend Error")
        except:
            st.error("❌ Backend Offline")
        
        # Quick actions
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("**🚀 Quick Actions:**")
        if st.button("🔄 Refresh Data"):
            st.session_state.curriculum_data = None
            st.session_state.analytics_data = None
            st.rerun()
        
        if st.button("📥 Export Curriculum"):
            st.info("Export feature coming soon!")
        
        if st.button("📤 Import Curriculum"):
            st.info("Import feature coming soon!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content based on selected page
    if page == "📊 Analytics":
        display_analytics_dashboard()
    
    elif page == "🏗️ Curriculum Builder":
        # Handle forms first
        if st.session_state.selected_lecture:
            display_topic_form()
        elif st.session_state.selected_topic:
            display_subtopic_form()
        else:
            display_curriculum_builder()
    
    elif page == "🧪 Preview & Test":
        st.subheader("🧪 Preview & Test Curriculum")
        st.info("🚧 Preview feature coming soon! This will allow you to test how the AI teaches your curriculum.")
        
        # Placeholder for preview functionality
        st.markdown("""
        **Planned Features:**
        - 🤖 Chat with AI using your curriculum
        - 📊 See how AI interprets your prompts
        - 🎯 Test understanding detection
        - 📝 Preview auto-generated notes
        """)
    
    elif page == "⚙️ Settings":
        st.subheader("⚙️ Dashboard Settings")
        st.info("🚧 Settings coming soon!")
        
        st.markdown("""
        **Planned Settings:**
        - 🎨 Theme customization
        - 🌍 Default language settings
        - 🔔 Notification preferences
        - 👥 User management
        - 🔐 Access controls
        """)

if __name__ == "__main__":
    main() 