import json
from sqlalchemy.orm import Session
from database import SessionLocal, create_tables
from database import Lecture, Topic, SubTopic

def create_python_curriculum():
    """Create initial Python programming curriculum"""
    
    curriculum = {
        "lectures": [
            {
                "title": "Python Fundamentals",
                "description": "Learn the basic building blocks of Python programming",
                "order_index": 1,
                "topics": [
                    {
                        "title": "Introduction to Python",
                        "description": "What is Python and why use it?",
                        "order_index": 1,
                        "learning_objectives": ["Understand what Python is", "Learn Python's advantages", "Set up Python environment"],
                        "estimated_duration_minutes": 30,
                        "subtopics": [
                            {
                                "title": "What is Python?",
                                "order_index": 1,
                                "content": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
                                "examples": [
                                    {"code": "print('Hello, World!')", "explanation": "Your first Python program"}
                                ],
                                "introduction_prompt": "Welcome! Let's start your Python journey. Python is one of the most popular programming languages because it's easy to learn and very powerful. Are you ready to see why Python is so loved by programmers?",
                                "explanation_prompt": "Think of Python as a language that lets you talk to computers in a way that's almost like talking to a human. It's designed to be readable and simple.",
                                "assessment_prompt": "Can you tell me in your own words what makes Python special as a programming language?"
                            },
                            {
                                "title": "Why Choose Python?",
                                "order_index": 2,
                                "content": "Python is versatile, has a large community, extensive libraries, and is beginner-friendly.",
                                "examples": [
                                    {"use_case": "Web Development", "example": "Django, Flask"},
                                    {"use_case": "Data Science", "example": "pandas, numpy"},
                                    {"use_case": "AI/ML", "example": "TensorFlow, scikit-learn"}
                                ],
                                "introduction_prompt": "Now that you know what Python is, let's explore why it's such a popular choice for beginners and experts alike.",
                                "explanation_prompt": "Python is like a Swiss Army knife of programming - it can do almost anything! From building websites to analyzing data to creating AI.",
                                "assessment_prompt": "What kind of projects or applications would you like to build with Python?"
                            }
                        ]
                    },
                    {
                        "title": "Variables and Data Types",
                        "description": "Learn how to store and work with different types of data",
                        "order_index": 2,
                        "learning_objectives": ["Create variables", "Understand different data types", "Convert between data types"],
                        "estimated_duration_minutes": 45,
                        "subtopics": [
                            {
                                "title": "Creating Variables",
                                "order_index": 1,
                                "content": "Variables are containers for storing data values. In Python, you create a variable by assigning a value to it.",
                                "examples": [
                                    {"code": "name = 'Alice'", "explanation": "Creates a string variable"},
                                    {"code": "age = 25", "explanation": "Creates an integer variable"},
                                    {"code": "height = 5.8", "explanation": "Creates a float variable"}
                                ],
                                "introduction_prompt": "Great! Now let's learn about variables - think of them as labeled boxes where you can store information. Ready to create your first variable?",
                                "explanation_prompt": "A variable is like giving a name to a piece of information so you can use it later. It's like putting a label on a box.",
                                "assessment_prompt": "Can you create a variable with your favorite color? What would that look like?"
                            },
                            {
                                "title": "Data Types",
                                "order_index": 2,
                                "content": "Python has several built-in data types: strings (text), integers (whole numbers), floats (decimal numbers), and booleans (True/False).",
                                "examples": [
                                    {"code": "text = 'Hello'  # string", "explanation": "Text data"},
                                    {"code": "number = 42    # integer", "explanation": "Whole numbers"},
                                    {"code": "price = 19.99  # float", "explanation": "Decimal numbers"},
                                    {"code": "is_active = True  # boolean", "explanation": "True or False values"}
                                ],
                                "introduction_prompt": "Excellent! Now let's explore the different types of data Python can work with. Each type has its own special purpose.",
                                "explanation_prompt": "Think of data types like different kinds of containers - some hold text, some hold numbers, some hold yes/no answers.",
                                "assessment_prompt": "If you wanted to store someone's name, age, and whether they like pizza, what data types would you use for each?"
                            }
                        ]
                    },
                    {
                        "title": "Basic Operations",
                        "description": "Learn arithmetic and string operations",
                        "order_index": 3,
                        "learning_objectives": ["Perform arithmetic operations", "Concatenate strings", "Use comparison operators"],
                        "estimated_duration_minutes": 40,
                        "subtopics": [
                            {
                                "title": "Arithmetic Operations",
                                "order_index": 1,
                                "content": "Python supports all basic arithmetic operations: addition (+), subtraction (-), multiplication (*), division (/), and more.",
                                "examples": [
                                    {"code": "result = 10 + 5  # Addition", "explanation": "result is 15"},
                                    {"code": "result = 20 - 8  # Subtraction", "explanation": "result is 12"},
                                    {"code": "result = 4 * 6   # Multiplication", "explanation": "result is 24"},
                                    {"code": "result = 15 / 3  # Division", "explanation": "result is 5.0"}
                                ],
                                "introduction_prompt": "Perfect! Now let's make Python do some math for us. Python is like a super-fast calculator that never makes mistakes.",
                                "explanation_prompt": "Just like in math class, Python follows the order of operations. You can add, subtract, multiply, and divide numbers easily.",
                                "assessment_prompt": "If you have 3 boxes with 8 items each, how would you calculate the total number of items using Python?"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Control Structures",
                "description": "Learn how to control the flow of your programs",
                "order_index": 2,
                "topics": [
                    {
                        "title": "Conditional Statements",
                        "description": "Make decisions in your code with if/else statements",
                        "order_index": 1,
                        "learning_objectives": ["Use if statements", "Understand elif and else", "Combine conditions"],
                        "estimated_duration_minutes": 50,
                        "subtopics": [
                            {
                                "title": "If Statements",
                                "order_index": 1,
                                "content": "If statements allow your program to make decisions based on conditions.",
                                "examples": [
                                    {"code": "if age >= 18:\n    print('You can vote!')", "explanation": "Checks if age is 18 or older"},
                                    {"code": "if temperature > 30:\n    print('It's hot today!')", "explanation": "Checks temperature condition"}
                                ],
                                "introduction_prompt": "Fantastic! Now let's give your programs the power to make decisions. This is where programming gets really exciting!",
                                "explanation_prompt": "An if statement is like asking a question - 'if this is true, then do that'. It's how programs make smart decisions.",
                                "assessment_prompt": "Can you think of a real-life situation where you'd want your program to make a decision based on some condition?"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    return curriculum

def seed_database():
    """Populate database with curriculum data"""
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_lectures = db.query(Lecture).count()
        if existing_lectures > 0:
            print("Database already contains curriculum data. Skipping seed.")
            return
        
        curriculum = create_python_curriculum()
        
        for lecture_data in curriculum["lectures"]:
            # Create lecture
            lecture = Lecture(
                title=lecture_data["title"],
                description=lecture_data["description"],
                order_index=lecture_data["order_index"]
            )
            db.add(lecture)
            db.flush()  # Get the lecture ID
            
            # Create topics
            for topic_data in lecture_data["topics"]:
                topic = Topic(
                    lecture_id=lecture.id,
                    title=topic_data["title"],
                    description=topic_data["description"],
                    order_index=topic_data["order_index"],
                    learning_objectives=json.dumps(topic_data["learning_objectives"]),
                    estimated_duration_minutes=topic_data["estimated_duration_minutes"]
                )
                db.add(topic)
                db.flush()  # Get the topic ID
                
                # Create subtopics
                for subtopic_data in topic_data["subtopics"]:
                    subtopic = SubTopic(
                        topic_id=topic.id,
                        title=subtopic_data["title"],
                        content=subtopic_data["content"],
                        examples=json.dumps(subtopic_data["examples"]),
                        order_index=subtopic_data["order_index"],
                        introduction_prompt=subtopic_data["introduction_prompt"],
                        explanation_prompt=subtopic_data["explanation_prompt"],
                        assessment_prompt=subtopic_data["assessment_prompt"]
                    )
                    db.add(subtopic)
        
        # Commit all changes
        db.commit()
        print("✅ Database seeded successfully with Python curriculum!")
        
        # Print summary
        lectures_count = db.query(Lecture).count()
        topics_count = db.query(Topic).count()
        subtopics_count = db.query(SubTopic).count()
        
        print(f"📚 Created {lectures_count} lectures")
        print(f"📖 Created {topics_count} topics")
        print(f"📝 Created {subtopics_count} subtopics")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 