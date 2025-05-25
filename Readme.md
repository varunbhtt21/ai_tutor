# 🐍 AI Python Tutor - P2

An intelligent, curriculum-driven AI tutoring system that adapts to student understanding and provides personalized Python learning experiences. **P2** introduces the **Teacher Dashboard** for complete curriculum control.

## 🎯 **Features**

### **P1: Curriculum-Driven Learning (Student Experience)**
- **🤖 AI-Driven Teaching**: AI leads conversations and guides learning paths
- **📚 Structured Curriculum**: Follow carefully designed sequences of topics and subtopics  
- **📊 Progress Tracking**: Real-time tracking with Red/Yellow/Green understanding levels
- **🎓 Personalized Learning**: Adapts to student understanding and pace
- **💾 Persistent Progress**: Learning journey is saved and continues where you left off
- **🌍 Multi-language Support**: Learn in 6 different languages

### **P2: Teacher Dashboard (NEW!)**
- **🏗️ Curriculum Builder**: Create and edit lectures, topics, and subtopics
- **🤖 AI Prompt Engineering**: Define how AI should introduce, explain, and assess concepts
- **📊 Analytics Dashboard**: Track student engagement and understanding patterns
- **🔄 Drag & Drop Reordering**: Easily reorganize curriculum structure
- **📋 Code Examples Management**: Add interactive examples for each concept
- **🎯 Learning Objectives**: Define clear goals for each topic
- **📈 Real-time Monitoring**: See how students progress through your curriculum

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Student App   │    │  Teacher Dashboard │    │   Backend API   │
│  (Port 8501)    │◄──►│   (Port 8502)    │◄──►│   (Port 8000)   │
│                 │    │                 │    │                 │
│ • Chat Interface│    │ • Curriculum    │    │ • FastAPI       │
│ • Progress View │    │   Builder       │    │ • SQLAlchemy    │
│ • Multi-language│    │ • Analytics     │    │ • OpenAI GPT-4o │
└─────────────────┘    │ • AI Prompts    │    │ • SQLite/Postgres│
     frontend/          └─────────────────┘    └─────────────────┘
     main.py                frontend/               backend/
                        teacher_dashboard.py        main.py
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- OpenAI API key
- UV package manager (recommended) or pip

### **1. Clone & Setup**
```bash
git clone https://github.com/varunbhtt21/ai_tutor.git
cd ai_tutor

# Copy environment template
cp backend/.env.template backend/.env
# Add your OpenAI API key to backend/.env
```

### **2. Start Backend**
```bash
./start_backend.sh
```

### **3. Start Student Frontend**
```bash
./start_frontend.sh
```

### **4. Start Teacher Dashboard (NEW!)**
```bash
./start_teacher_dashboard.sh
```

## 🎓 **For Teachers: Building Your Curriculum**

### **Access Teacher Dashboard**
1. Start the backend and teacher dashboard
2. Open http://localhost:8502
3. Navigate to "🏗️ Curriculum Builder"

### **Creating Content**
1. **Lectures**: High-level course modules
2. **Topics**: Specific learning areas within lectures  
3. **Subtopics**: Granular concepts with AI teaching prompts

### **AI Prompt Engineering**
For each subtopic, define:
- **Introduction Prompt**: How AI should introduce the concept
- **Explanation Prompt**: How AI should explain when students ask questions
- **Assessment Prompt**: How AI should check understanding

### **Example AI Prompts**
```
Introduction: "Welcome! Let's explore Python variables. Think of them as labeled boxes where you store information. Ready to see how they work?"

Explanation: "A variable is like giving a name to a piece of information so you can use it later. It's like putting a label on a box."

Assessment: "Can you create a variable with your favorite color? What would that look like?"
```

## 📊 **Analytics & Monitoring**

The Teacher Dashboard provides insights into:
- **Student Engagement**: Active students, conversation counts
- **Understanding Patterns**: Red/Yellow/Green distribution
- **Progress Tracking**: Completion rates across topics
- **Curriculum Effectiveness**: Which topics need improvement

## 🛠️ **Development**

### **Project Structure**
```
ai_tutor/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── database.py         # Database models
│   ├── ai_tutor_service.py # AI tutoring logic
│   ├── teacher_service.py  # Teacher management (NEW!)
│   └── curriculum_seed.py  # Initial curriculum data
├── frontend/               # Streamlit applications
│   ├── main.py            # Student learning interface
│   ├── teacher_dashboard.py # Teacher curriculum builder (NEW!)
│   └── requirements.txt    # Shared frontend dependencies
└── scripts/               # Startup scripts
```

### **API Endpoints**

#### **Student Learning**
- `POST /learning/start` - Start curriculum-driven session
- `POST /learning/respond` - Process student response
- `GET /student/{id}/progress` - Get student progress

#### **Teacher Management (NEW!)**
- `GET /teacher/curriculum` - Get full curriculum structure
- `GET /teacher/analytics` - Get usage analytics
- `POST /teacher/lectures` - Create lecture
- `POST /teacher/topics` - Create topic
- `POST /teacher/subtopics` - Create subtopic
- `PUT /teacher/{type}/{id}` - Update content
- `DELETE /teacher/{type}/{id}` - Delete content

## 🔄 **Migration from P1 to P2**

Existing P1 installations automatically gain P2 features:
- All existing curriculum data is preserved
- Student progress continues seamlessly
- New teacher endpoints are added alongside existing ones
- No breaking changes to student experience

## 🌟 **What's Next?**

### **P3 Roadmap**
- **🧪 Curriculum Preview**: Test AI teaching before publishing
- **👥 Multi-teacher Collaboration**: Team curriculum development
- **📤 Import/Export**: Share curricula between institutions
- **🎨 Custom Themes**: Branded learning experiences
- **🔐 User Management**: Role-based access control
- **📱 Mobile App**: Native iOS/Android applications

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with both student and teacher interfaces
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details.

## 🆘 **Support**

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [your-email@domain.com]

---

**Transform your teaching with AI-driven, personalized education! 🚀**

