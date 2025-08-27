API Usage Examples
=================

This page provides comprehensive examples of how to use the Canvas Quiz Manager API endpoints for common tasks.

Question Management
------------------

Creating a New Question
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import httpx
    import asyncio

    async def create_question():
        """Create a new multiple choice question"""
        
        question_data = {
            "question_text": "What is the capital of France?",
            "question_type": "multiple_choice_question",
            "topic": "geography",
            "tags": "capitals,europe,france",
            "learning_objective": "Understand European geography",
            "points_possible": 1.0,
            "neutral_comments": "Paris is the capital and largest city of France.",
            "answers": [
                {
                    "id": 1,
                    "text": "London",
                    "html": "<p>London</p>",
                    "comments": "London is the capital of England, not France.",
                    "comments_html": "<p>London is the capital of England, not France.</p>",
                    "weight": 0.0
                },
                {
                    "id": 2,
                    "text": "Paris",
                    "html": "<p>Paris</p>",
                    "comments": "Correct! Paris is the capital of France.",
                    "comments_html": "<p>Correct! Paris is the capital of France.</p>",
                    "weight": 100.0
                },
                {
                    "id": 3,
                    "text": "Berlin",
                    "html": "<p>Berlin</p>",
                    "comments": "Berlin is the capital of Germany, not France.",
                    "comments_html": "<p>Berlin is the capital of Germany, not France.</p>",
                    "weight": 0.0
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/questions",
                json=question_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Question created successfully: {result}")
            else:
                print(f"Error creating question: {response.text}")

    # Run the example
    asyncio.run(create_question())

Updating an Existing Question
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def update_question(question_id: int):
        """Update an existing question with new feedback"""
        
        update_data = {
            "question_text": "What is the capital of France?",
            "topic": "geography",
            "tags": "capitals,europe,france,updated",
            "learning_objective": "Understand European geography and culture",
            "correct_comments": "Excellent! Paris is indeed the capital of France.",
            "incorrect_comments": "Remember that Paris is the capital of France.",
            "neutral_comments": "Paris is the capital and largest city of France, known for its rich history and culture.",
            "correct_comments_html": "<p>Excellent! Paris is indeed the capital of France.</p>",
            "incorrect_comments_html": "<p>Remember that Paris is the capital of France.</p>",
            "neutral_comments_html": "<p>Paris is the capital and largest city of France, known for its rich history and culture.</p>",
            "answers": [
                {
                    "id": 1,
                    "text": "London",
                    "html": "<p>London</p>",
                    "comments": "London is the capital of England, not France.",
                    "comments_html": "<p>London is the capital of England, not France.</p>",
                    "weight": 0.0
                },
                {
                    "id": 2,
                    "text": "Paris",
                    "html": "<p>Paris</p>",
                    "comments": "Correct! Paris is the capital of France.",
                    "comments_html": "<p>Correct! Paris is the capital of France.</p>",
                    "weight": 100.0
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"http://localhost:8000/api/questions/{question_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Question updated successfully: {result}")
            else:
                print(f"Error updating question: {response.text}")

AI-Powered Feedback Generation
-----------------------------

Generating Feedback for a Question
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def generate_ai_feedback(question_id: int):
        """Generate AI-powered feedback for a question"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000/api/questions/{question_id}/generate-feedback"
            )
            
            if response.status_code == 200:
                feedback = response.json()
                print("Generated Feedback:")
                print(f"General Feedback: {feedback['general_feedback']}")
                print(f"Answer Feedback: {feedback['answer_feedback']}")
                print(f"Token Usage: {feedback['token_usage']}")
            else:
                print(f"Error generating feedback: {response.text}")

Chat Assistant
--------------

Sending a Message to the Chat Assistant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def chat_with_assistant(message: str):
        """Send a message to the AI chat assistant"""
        
        chat_data = {
            "message": message,
            "history": []  # Optional: include previous messages
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/chat",
                json=chat_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Assistant: {result['response']}")
                return result['response']
            else:
                print(f"Error in chat: {response.text}")
                return None

    # Example usage
    async def example_chat():
        await chat_with_assistant("What is accessibility in web design?")
        await chat_with_assistant("Can you give me examples of accessible HTML elements?")

Canvas Integration
-----------------

Fetching Courses from Canvas
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def fetch_canvas_courses():
        """Fetch available courses from Canvas LMS"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/courses")
            
            if response.status_code == 200:
                result = response.json()
                courses = result['courses']
                print(f"Found {len(courses)} courses:")
                for course in courses:
                    print(f"- {course['name']} (ID: {course['id']})")
                return courses
            else:
                print(f"Error fetching courses: {response.text}")
                return []

Fetching Quizzes from a Course
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def fetch_course_quizzes(course_id: str):
        """Fetch quizzes from a specific Canvas course"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8000/api/courses/{course_id}/quizzes"
            )
            
            if response.status_code == 200:
                result = response.json()
                quizzes = result['quizzes']
                print(f"Found {len(quizzes)} quizzes in course {course_id}:")
                for quiz in quizzes:
                    print(f"- {quiz['title']} (ID: {quiz['id']})")
                return quizzes
            else:
                print(f"Error fetching quizzes: {response.text}")
                return []

System Configuration
-------------------

Updating System Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def update_system_config():
        """Update system configuration settings"""
        
        config_data = {
            "course_id": "12345",
            "quiz_id": "67890"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/configuration",
                json=config_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Configuration updated: {result}")
            else:
                print(f"Error updating configuration: {response.text}")

Managing System Prompts
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def update_system_prompt():
        """Update the AI system prompt"""
        
        new_prompt = """
        You are an educational assistant helping with quiz questions. 
        Provide clear, educational feedback that helps students understand 
        the concepts being tested. Be encouraging but accurate.
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/system-prompt",
                data={"prompt": new_prompt}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"System prompt updated: {result}")
            else:
                print(f"Error updating system prompt: {response.text}")

Learning Objectives Management
-----------------------------

Managing Learning Objectives
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def manage_objectives():
        """Create and manage learning objectives"""
        
        objectives_data = {
            "objectives": [
                {
                    "text": "Understand web accessibility principles",
                    "blooms_level": "understand",
                    "priority": "high"
                },
                {
                    "text": "Apply accessibility guidelines to HTML",
                    "blooms_level": "apply",
                    "priority": "medium"
                },
                {
                    "text": "Evaluate website accessibility",
                    "blooms_level": "evaluate",
                    "priority": "high"
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/objectives",
                json=objectives_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Objectives updated: {result}")
            else:
                print(f"Error updating objectives: {response.text}")

Error Handling Examples
----------------------

Handling API Errors
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def robust_api_call():
        """Example of robust API error handling"""
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8000/api/questions")
                
                if response.status_code == 200:
                    questions = response.json()
                    print(f"Successfully loaded {len(questions)} questions")
                elif response.status_code == 404:
                    print("Questions endpoint not found")
                elif response.status_code == 500:
                    print("Server error occurred")
                else:
                    print(f"Unexpected status code: {response.status_code}")
                    
            except httpx.ConnectError:
                print("Could not connect to the server")
            except httpx.TimeoutException:
                print("Request timed out")
            except Exception as e:
                print(f"Unexpected error: {e}")

Complete Workflow Example
------------------------

Full Question Lifecycle
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def complete_question_workflow():
        """Complete workflow: create, update, generate feedback, and chat"""
        
        # 1. Create a new question
        question_data = {
            "question_text": "What is the purpose of the alt attribute in HTML?",
            "question_type": "multiple_choice_question",
            "topic": "accessibility",
            "tags": "html,accessibility,alt",
            "learning_objective": "Understand HTML accessibility features",
            "points_possible": 2.0,
            "answers": [
                {
                    "id": 1,
                    "text": "To make images load faster",
                    "weight": 0.0
                },
                {
                    "id": 2,
                    "text": "To provide alternative text for screen readers",
                    "weight": 100.0
                },
                {
                    "id": 3,
                    "text": "To change image colors",
                    "weight": 0.0
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            # Create question
            create_response = await client.post(
                "http://localhost:8000/api/questions",
                json=question_data
            )
            
            if create_response.status_code == 200:
                question = create_response.json()
                question_id = question['id']
                print(f"Created question with ID: {question_id}")
                
                # Generate AI feedback
                feedback_response = await client.post(
                    f"http://localhost:8000/api/questions/{question_id}/generate-feedback"
                )
                
                if feedback_response.status_code == 200:
                    feedback = feedback_response.json()
                    print("Generated AI feedback successfully")
                
                # Chat about the question
                chat_response = await client.post(
                    "http://localhost:8000/api/chat",
                    json={"message": f"Tell me more about question {question_id}"}
                )
                
                if chat_response.status_code == 200:
                    chat_result = chat_response.json()
                    print(f"Chat response: {chat_result['response']}")
                
                # Update the question with feedback
                update_data = question_data.copy()
                update_data["correct_comments"] = feedback.get("general_feedback", "")
                
                update_response = await client.put(
                    f"http://localhost:8000/api/questions/{question_id}",
                    json=update_data
                )
                
                if update_response.status_code == 200:
                    print("Question updated with AI feedback")
                
                print("Complete workflow finished successfully!")
            else:
                print(f"Error in workflow: {create_response.text}")

    # Run the complete workflow
    asyncio.run(complete_question_workflow())
