import streamlit as st
import requests
import os
import json
import re
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional, Tuple
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
    .validation-error {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .validation-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .validation-success {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .template-box {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        padding: 1rem;
        border-radius: 4px;
        font-family: monospace;
        white-space: pre-line;
        color: #333;
        font-size: 14px;
        line-height: 1.4;
    }
    .lecture-card {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
    }
    .subtopic-preview {
        background-color: #f3e5f5;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #9c27b0;
        margin: 0.3rem 0 0.3rem 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ContentValidator:
    """Validates Notion-style content against template structure"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
    
    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate pasted content against template"""
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        if not content.strip():
            self.errors.append("Content cannot be empty")
            return self._build_result()
        
        # Check required headers
        self._validate_headers(content)
        
        # Check subtopic structure
        self._validate_subtopics(content)
        
        # Check content completeness
        self._validate_content_completeness(content)
        
        return self._build_result()
    
    def _validate_headers(self, content: str):
        """Validate lecture title and description headers"""
        title_pattern = r'### Lecture Title\s*:\s*(.+)'
        title_match = re.search(title_pattern, content, re.IGNORECASE)
        
        if not title_match:
            self.errors.append("Missing required header: '### Lecture Title :'")
            self.suggestions.append("Add '### Lecture Title : Your Title Here' at the beginning")
        elif not title_match.group(1).strip():
            self.errors.append("Lecture title cannot be empty")
            self.suggestions.append("Provide a meaningful title after '### Lecture Title :'")
        
        # Description is optional, but validate format if present
        desc_pattern = r'### Description\s*:\s*(.+)'
        desc_match = re.search(desc_pattern, content, re.IGNORECASE)
        if desc_match and not desc_match.group(1).strip():
            self.warnings.append("Description header found but content is empty")
    
    def _validate_subtopics(self, content: str):
        """Validate subtopic numbering and structure"""
        subtopic_pattern = r'# \$(\d+)'
        subtopic_matches = re.findall(subtopic_pattern, content)
        
        if not subtopic_matches:
            self.errors.append("No subtopics found. Must have at least '# $1'")
            self.suggestions.append("Add subtopic sections using '# $1', '# $2', etc.")
            return
        
        # Check sequential numbering
        numbers = [int(match) for match in subtopic_matches]
        expected = list(range(1, len(numbers) + 1))
        
        if numbers != expected:
            self.errors.append(f"Subtopics must be numbered sequentially starting from $1. Found: ${', $'.join(map(str, numbers))}")
            self.suggestions.append(f"Use sequential numbering: ${', $'.join(map(str, expected))}")
        
        # Check for duplicates
        if len(numbers) != len(set(numbers)):
            duplicates = [f"${n}" for n in set(numbers) if numbers.count(n) > 1]
            self.errors.append(f"Duplicate subtopic numbers found: {', '.join(duplicates)}")
            self.suggestions.append("Each subtopic number should be unique")
        
        # Check if starts with $1
        if numbers and numbers[0] != 1:
            self.errors.append("First subtopic must be '# $1'")
            self.suggestions.append("Start subtopic numbering with '# $1'")
    
    def _validate_content_completeness(self, content: str):
        """Check if subtopics have content"""
        # Split by subtopic markers
        sections = re.split(r'# \$\d+', content)
        
        if len(sections) > 1:  # Skip header section
            subtopic_sections = sections[1:]
            
            for i, section in enumerate(subtopic_sections, 1):
                section_content = section.strip()
                if not section_content:
                    self.warnings.append(f"Subtopic ${i} appears to be empty")
                    self.suggestions.append(f"Add content after '# ${i}' marker")
                elif len(section_content) < 20:
                    self.warnings.append(f"Subtopic ${i} seems very short (less than 20 characters)")
    
    def _build_result(self) -> Dict[str, Any]:
        """Build validation result dictionary"""
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }

class ContentParser:
    """Parses validated Notion-style content into structured curriculum"""
    
    @staticmethod
    def parse_content(content: str) -> Dict[str, Any]:
        """Parse Notion-style content into structured curriculum"""
        
        # Extract lecture title and description
        title_match = re.search(r'### Lecture Title\s*:\s*(.+)', content, re.IGNORECASE)
        desc_match = re.search(r'### Description\s*:\s*(.+)', content, re.IGNORECASE)
        
        title = title_match.group(1).strip() if title_match else "Untitled Lecture"
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract subtopics
        subtopics = ContentParser._parse_subtopics(content)
        
        return {
            "title": title,
            "description": description,
            "subtopics": subtopics,
            "total_subtopics": len(subtopics)
        }
    
    @staticmethod
    def _parse_subtopics(content: str) -> List[Dict[str, Any]]:
        """Parse individual subtopic sections"""
        subtopics = []
        
        # Split content by subtopic markers
        parts = re.split(r'# \$(\d+)', content)
        
        # Skip the header part (before first $1)
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    order_index = int(parts[i])
                    subtopic_content = parts[i + 1].strip()
                    
                    # Extract title from first heading in content
                    title = ContentParser._extract_subtopic_title(subtopic_content, order_index)
                    
                    # Extract code examples
                    code_examples = ContentParser._extract_code_blocks(subtopic_content)
                    
                    # Extract inquiry prompts
                    inquiry_prompts = ContentParser._extract_inquiry_prompts(subtopic_content)
                    
                    subtopics.append({
                        "order_index": order_index,
                        "title": title,
                        "content": subtopic_content,
                        "examples": code_examples,
                        "inquiry_prompts": inquiry_prompts,
                        "estimated_duration_minutes": ContentParser._estimate_duration(subtopic_content)
                    })
        
        return subtopics
    
    @staticmethod
    def _extract_subtopic_title(content: str, order_index: int) -> str:
        """Extract title from subtopic content"""
        # Look for markdown headings
        heading_match = re.search(r'^##\s*(.+)', content, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
            # Remove time indicators like [10 min]
            title = re.sub(r'\[.*?\]', '', title).strip()
            return title
        
        # Fallback to first line if no heading found
        first_line = content.split('\n')[0].strip()
        if first_line and len(first_line) < 100:
            return first_line
        
        return f"Subtopic {order_index}"
    
    @staticmethod
    def _extract_code_blocks(content: str) -> List[Dict[str, str]]:
        """Extract code examples from content"""
        code_blocks = []
        
        # Find code blocks with ```python or ```
        pattern = r'```(?:python)?\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, code in enumerate(matches):
            # Look for explanation before or after the code block
            explanation = f"Code example {i + 1}"
            
            code_blocks.append({
                "code": code.strip(),
                "explanation": explanation
            })
        
        return code_blocks
    
    @staticmethod
    def _extract_inquiry_prompts(content: str) -> List[str]:
        """Extract inquiry prompts from content"""
        prompts = []
        
        # Look for quoted text that might be prompts
        quote_pattern = r'[">]\s*"([^"]+)"'
        matches = re.findall(quote_pattern, content)
        
        for match in matches:
            if len(match) > 10:  # Filter out short quotes
                prompts.append(match.strip())
        
        return prompts
    
    @staticmethod
    def _estimate_duration(content: str) -> int:
        """Estimate duration based on content length"""
        # Look for explicit duration markers
        duration_match = re.search(r'\[(\d+)\s*min\]', content)
        if duration_match:
            return int(duration_match.group(1))
        
        # Estimate based on content length
        word_count = len(content.split())
        # Assume 150 words per minute reading + time for examples
        estimated_minutes = max(5, word_count // 100 * 5)
        return min(estimated_minutes, 60)  # Cap at 60 minutes

def initialize_session_state():
    """Initialize session state for teacher dashboard"""
    if 'content_input' not in st.session_state:
        st.session_state.content_input = ""
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None
    if 'parsed_content' not in st.session_state:
        st.session_state.parsed_content = None
    if 'show_template' not in st.session_state:
        st.session_state.show_template = False

def get_template_example():
    """Return the template example"""
    return """### Lecture Title : Comparison Operators

### Description : Learn about Python comparison operators and how to use them

# $1

## What are Comparison Operators? [10 min]

**Inquiry Prompt:**

> "When you compare two numbers—like checking if one is bigger or smaller—what kind of result do you expect?"

Students might guess: *"Yes or No,"* *"True or False,"* or similar.

### Explanation

Comparison operators compare two values and **always return a boolean** (`True` or `False` in Python).

- **> (Greater Than)**
- **>= (Greater Than Equal To)**
- **< (Less Than)**
- **<= (Less Than Equal To)**
- **== (Equal To)**
- **!= (Not Equal To)**

# $2

## Greater Than Operator (`>`)

**Inquiry Prompt:**

> "How do we check if one number is strictly larger than another? For example, is 5 greater than 4?"

```python
a = 5
b = 4
print(a > b)   # Outputs True
```

If the first value is less than or equal to the second:

```python
a = 5
b = 5
print(a > b)   # Outputs False
```

### Student Task

Check if Sunil passed an exam. Passing mark = 35.

```python
sunil_marks = 36
passing_marks = 35

is_passed = sunil_marks > passing_marks
print(is_passed)   # True => Sunil is passed
```"""

def display_validation_results(validation_result: Dict[str, Any]):
    """Display validation results with appropriate styling"""
    if validation_result["is_valid"]:
        st.markdown('<div class="validation-success">✅ <strong>Content is valid!</strong> Ready to import.</div>', 
                   unsafe_allow_html=True)
    else:
        # Display errors
        if validation_result["errors"]:
            st.markdown('<div class="validation-error">', unsafe_allow_html=True)
            st.markdown("**❌ ERRORS (Must fix before importing):**")
            for error in validation_result["errors"]:
                st.markdown(f"• {error}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display warnings
        if validation_result["warnings"]:
            st.markdown('<div class="validation-warning">', unsafe_allow_html=True)
            st.markdown("**⚠️ WARNINGS (Recommended to fix):**")
            for warning in validation_result["warnings"]:
                st.markdown(f"• {warning}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display suggestions
        if validation_result["suggestions"]:
            st.markdown("**💡 SUGGESTIONS:**")
            for suggestion in validation_result["suggestions"]:
                st.markdown(f"• {suggestion}")

def create_lecture_from_parsed_content(parsed_content: Dict[str, Any], custom_prompt: str = "") -> bool:
    """Create lecture in backend from parsed content"""
    try:
        # First create the lecture
        lecture_payload = {
            "title": parsed_content["title"],
            "description": parsed_content["description"],
            "order_index": 1  # Will be auto-incremented by backend
        }
        
        lecture_response = requests.post(f"{API_BASE_URL}/teacher/lectures", json=lecture_payload)
        if lecture_response.status_code != 200:
            st.error(f"Failed to create lecture: {lecture_response.text}")
            return False
        
        lecture_data = lecture_response.json()
        lecture_id = lecture_data["id"]
        
        # Create a single topic for all subtopics
        topic_payload = {
            "lecture_id": lecture_id,
            "title": parsed_content["title"],
            "description": parsed_content["description"],
            "order_index": 1,
            "learning_objectives": [f"Complete {parsed_content['title']} subtopics"],
            "estimated_duration_minutes": sum(st.get("estimated_duration_minutes", 30) for st in parsed_content["subtopics"])
        }
        
        topic_response = requests.post(f"{API_BASE_URL}/teacher/topics", json=topic_payload)
        if topic_response.status_code != 200:
            st.error(f"Failed to create topic: {topic_response.text}")
            return False
        
        topic_data = topic_response.json()
        topic_id = topic_data["id"]
        
        # Create subtopics
        for subtopic in parsed_content["subtopics"]:
            subtopic_payload = {
                "topic_id": topic_id,
                "title": subtopic["title"],
                "content": subtopic["content"],
                "order_index": subtopic["order_index"],
                "examples": subtopic["examples"],
                "introduction_prompt": custom_prompt if custom_prompt else None,
                "explanation_prompt": None,
                "assessment_prompt": None
            }
            
            subtopic_response = requests.post(f"{API_BASE_URL}/teacher/subtopics", json=subtopic_payload)
            if subtopic_response.status_code != 200:
                st.error(f"Failed to create subtopic {subtopic['title']}: {subtopic_response.text}")
                return False
        
        return True
        
    except Exception as e:
        st.error(f"Error creating lecture: {str(e)}")
        return False

def fetch_curriculum_overview():
    """Fetch curriculum overview from API"""
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

def display_content_import_page():
    """Display the content import page"""
    st.subheader("📝 Import Lecture Content")
    
    # Template helper
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("📋 Show Template", key="show_template_btn"):
            st.session_state.show_template = not st.session_state.show_template
    
    if st.session_state.show_template:
        with st.expander("📋 Template Guide", expanded=True):
            st.markdown("**Required Structure:**")
            st.code(get_template_example(), language="markdown")
            
            st.markdown("**Rules:**")
            st.markdown("""
            - ✅ Start with `### Lecture Title : Your Title Here`
            - ✅ Use `# $1`, `# $2`, `# $3`... for subtopics
            - ✅ Number subtopics sequentially
            - ✅ Add content after each `# $N` marker
            - ⚠️ Description is optional
            """)
            
            if st.button("📋 Copy Template"):
                st.session_state.content_input = get_template_example()
                st.rerun()
    
    # Content input area
    st.markdown("**Paste your Notion content here:**")
    content_input = st.text_area(
        "Content",
        value=st.session_state.content_input,
        height=400,
        placeholder="Paste your lecture content following the template structure...",
        label_visibility="collapsed"
    )
    
    # Update session state
    if content_input != st.session_state.content_input:
        st.session_state.content_input = content_input
        st.session_state.validation_result = None
        st.session_state.parsed_content = None
    
    # Validation and parsing
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔍 Validate Content", type="primary"):
            if content_input.strip():
                validator = ContentValidator()
                st.session_state.validation_result = validator.validate_content(content_input)
                
                if st.session_state.validation_result["is_valid"]:
                    parser = ContentParser()
                    st.session_state.parsed_content = parser.parse_content(content_input)
            else:
                st.error("Please paste some content first")
    
    with col2:
        if st.button("👀 Preview Content"):
            if content_input.strip():
                # Always try to parse for preview, even if validation fails
                try:
                    parser = ContentParser()
                    st.session_state.parsed_content = parser.parse_content(content_input)
                    
                    # Also run validation to show any issues
                    validator = ContentValidator()
                    st.session_state.validation_result = validator.validate_content(content_input)
                    
                    st.info("💡 Preview generated! Check validation results below.")
                except Exception as e:
                    st.error(f"Failed to parse content: {str(e)}")
            else:
                st.error("Please paste some content first")
    
    # Display validation results
    if st.session_state.validation_result:
        st.markdown("---")
        st.markdown("### 🔍 Validation Results")
        display_validation_results(st.session_state.validation_result)
    
    # Preview parsed content
    if st.session_state.parsed_content:
        st.markdown("---")
        st.markdown("### 👀 Content Preview")
        
        parsed = st.session_state.parsed_content
        
        # Main metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lecture Title", parsed["title"])
        with col2:
            st.metric("Subtopics", parsed["total_subtopics"])
        with col3:
            total_duration = sum(st.get("estimated_duration_minutes", 30) for st in parsed["subtopics"])
            st.metric("Est. Duration", f"{total_duration} min")
        
        if parsed["description"]:
            st.markdown(f"**Description:** {parsed['description']}")
        
        # Detailed subtopics preview
        st.markdown("**📚 Subtopics Structure:**")
        
        for subtopic in parsed["subtopics"]:
            with st.expander(f"${subtopic['order_index']}. {subtopic['title']} ({subtopic['estimated_duration_minutes']} min)", expanded=False):
                
                # Content preview
                st.markdown("**📝 Content Preview:**")
                content_lines = subtopic['content'].split('\n')[:5]  # First 5 lines
                preview_text = '\n'.join(content_lines)
                if len(subtopic['content'].split('\n')) > 5:
                    preview_text += "\n... (content continues)"
                st.text(preview_text)
                
                # Code examples
                if subtopic["examples"]:
                    st.markdown(f"**💻 Code Examples ({len(subtopic['examples'])}):**")
                    for i, example in enumerate(subtopic["examples"][:2], 1):  # Show first 2 examples
                        st.markdown(f"*Example {i}:*")
                        st.code(example["code"], language="python")
                        st.caption(example["explanation"])
                    
                    if len(subtopic["examples"]) > 2:
                        st.caption(f"... and {len(subtopic['examples']) - 2} more examples")
                
                # Inquiry prompts
                if subtopic["inquiry_prompts"]:
                    st.markdown(f"**❓ Inquiry Prompts ({len(subtopic['inquiry_prompts'])}):**")
                    for prompt in subtopic["inquiry_prompts"][:2]:  # Show first 2 prompts
                        st.markdown(f'> "{prompt}"')
                    
                    if len(subtopic["inquiry_prompts"]) > 2:
                        st.caption(f"... and {len(subtopic['inquiry_prompts']) - 2} more prompts")
                
                # Content statistics
                word_count = len(subtopic['content'].split())
                st.caption(f"📊 Stats: {word_count} words, {len(subtopic['content'])} characters")
        
        # Show import readiness
        if st.session_state.validation_result:
            if st.session_state.validation_result["is_valid"]:
                st.success("✅ Content is ready for import!")
            else:
                st.warning("⚠️ Fix validation errors above before importing.")
        else:
            st.info("💡 Run validation to check if content is ready for import.")
    
    # Custom AI prompt and import (only show when content is valid)
    if (st.session_state.parsed_content and 
        st.session_state.validation_result and 
        st.session_state.validation_result["is_valid"]):
        
        st.markdown("---")
        st.markdown("### 🤖 Optional AI Teaching Prompt")
        custom_prompt = st.text_area(
            "Custom instructions for AI tutor (optional)",
            placeholder="e.g., 'Focus on practical examples and encourage students to ask questions...'",
            height=100
        )
        
        # Import button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📚 Import Lecture", type="primary"):
                with st.spinner("Creating lecture..."):
                    if create_lecture_from_parsed_content(st.session_state.parsed_content, custom_prompt):
                        st.success("✅ Lecture imported successfully!")
                        # Clear the form
                        st.session_state.content_input = ""
                        st.session_state.validation_result = None
                        st.session_state.parsed_content = None
                        st.rerun()
        
        with col2:
            st.info("💡 Make sure to validate your content before importing to ensure it follows the template structure.")

def display_curriculum_overview_page():
    """Display curriculum overview page"""
    st.subheader("📚 Curriculum Overview")
    
    curriculum = fetch_curriculum_overview()
    if not curriculum:
        st.error("Failed to load curriculum data")
        return
    
    lectures = curriculum.get("lectures", [])
    
    if not lectures:
        st.info("No lectures found. Import your first lecture using the Content Import page!")
        return
    
    # Summary metrics
    total_lectures = len(lectures)
    total_topics = sum(len(lecture.get("topics", [])) for lecture in lectures)
    total_subtopics = sum(
        len(topic.get("subtopics", [])) 
        for lecture in lectures 
        for topic in lecture.get("topics", [])
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Lectures", total_lectures)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Topics", total_topics)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Subtopics", total_subtopics)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display lectures
    for lecture in lectures:
        st.markdown('<div class="lecture-card">', unsafe_allow_html=True)
        st.markdown(f"**📚 {lecture['title']}**")
        if lecture.get('description'):
            st.markdown(f"*{lecture['description']}*")
        
        topics = lecture.get('topics', [])
        if topics:
            st.markdown(f"**Topics ({len(topics)}):**")
            for topic in topics:
                subtopics = topic.get('subtopics', [])
                st.markdown(f"• **{topic['title']}** - {len(subtopics)} subtopics")
                
                # Show subtopics in expandable section
                if subtopics:
                    with st.expander(f"View {len(subtopics)} subtopics"):
                        for subtopic in subtopics:
                            st.markdown('<div class="subtopic-preview">', unsafe_allow_html=True)
                            st.markdown(f"**${subtopic.get('order_index', '?')}. {subtopic['title']}**")
                            
                            # Show content preview (first 100 chars)
                            content_preview = subtopic.get('content', '')[:100]
                            if len(content_preview) == 100:
                                content_preview += "..."
                            st.caption(content_preview)
                            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")

def main():
    """Main teacher dashboard application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">👩‍🏫 AI Tutor - Teacher Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Import and manage your AI-driven curriculum</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🎛️ Dashboard Navigation")
        
        page = st.selectbox(
            "Select Page",
            ["📝 Content Import", "📚 Curriculum Overview", "🧪 Preview & Test", "⚙️ Settings"]
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
        
        # Quick info
        st.markdown("---")
        st.markdown("**📋 Template Format:**")
        st.code("""### Lecture Title : Title
### Description : Desc

# $1
Content here...

# $2
More content...""")
        
        st.markdown("**🎯 Features:**")
        st.markdown("""
        - ✅ Notion-style import
        - 🔍 Content validation
        - 🤖 AI prompt customization
        - 📊 Curriculum overview
        """)
    
    # Main content based on selected page
    if page == "📝 Content Import":
        display_content_import_page()
    
    elif page == "📚 Curriculum Overview":
        display_curriculum_overview_page()
    
    elif page == "🧪 Preview & Test":
        st.subheader("🧪 Preview & Test Curriculum")
        st.info("🚧 Preview feature coming soon! This will allow you to test how the AI teaches your curriculum.")
        
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