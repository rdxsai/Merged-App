Module Organization
==================

This document describes the modular architecture of the Canvas Quiz Manager application.

Overview
--------

The application is organized into focused modules for better maintainability, testability, and scalability. Each module has a specific responsibility and clear interfaces.

Package Structure
----------------

.. code-block:: text

   src/question_app/
   ├── __init__.py              # Package initialization
   ├── main.py                  # FastAPI application and router integration
   ├── api/                     # API endpoints and routers
   │   ├── __init__.py          # API module exports
   │   └── canvas.py            # Canvas LMS integration endpoints
   ├── models/                  # Data models and schemas
   │   ├── __init__.py
   │   ├── question.py          # Question-related models
   │   └── objective.py         # Learning objective models
   ├── utils/                   # Utility functions
   │   ├── __init__.py
   │   ├── file_utils.py        # File I/O operations
   │   └── text_utils.py        # Text processing utilities
   ├── core/                    # Core configuration (planned)
   └── services/                # Business logic (planned)

Models Package
-------------

The ``models`` package contains all Pydantic data models used throughout the application.

Question Models
~~~~~~~~~~~~~~

**File**: ``models/question.py``

Contains models for quiz questions and answers:

- ``Answer``: Represents a quiz answer option with text, HTML, comments, and weight
- ``Question``: Complete quiz question with all metadata and answer options
- ``QuestionUpdate``: Model for updating existing questions
- ``NewQuestion``: Model for creating new questions

**Usage**:

.. code-block:: python

   from question_app.models import Question, Answer, QuestionUpdate

   # Create a new question
   question = Question(
       id=1,
       quiz_id=123,
       question_text="What is 2+2?",
       points_possible=1.0,
       answers=[Answer(id=1, text="4", weight=100.0)]
   )

Objective Models
~~~~~~~~~~~~~~~

**File**: ``models/objective.py``

Contains models for learning objectives:

- ``LearningObjective``: Represents a learning objective with text, Bloom's level, and priority
- ``ObjectivesUpdate``: Model for updating learning objectives

**Usage**:

.. code-block:: python

   from question_app.models import LearningObjective, ObjectivesUpdate

   # Create a learning objective
   objective = LearningObjective(
       text="Understand basic arithmetic",
       blooms_level="understand",
       priority="medium"
   )

Utils Package
------------

The ``utils`` package contains utility functions organized by functionality.

File Utilities
~~~~~~~~~~~~~

**File**: ``utils/file_utils.py``

Handles all file I/O operations for data persistence:

- ``load_questions()``: Load questions from JSON file
- ``save_questions()``: Save questions to JSON file
- ``load_objectives()``: Load learning objectives from JSON file
- ``save_objectives()``: Save learning objectives to JSON file
- ``load_system_prompt()``: Load AI system prompt from file
- ``save_system_prompt()``: Save AI system prompt to file
- ``load_chat_system_prompt()``: Load chat system prompt from file
- ``save_chat_system_prompt()``: Save chat system prompt to file
- ``load_welcome_message()``: Load chat welcome message from file
- ``save_welcome_message()``: Save chat welcome message to file
- ``get_default_chat_system_prompt()``: Get default chat system prompt
- ``get_default_welcome_message()``: Get default welcome message

**Usage**:

.. code-block:: python

   from question_app.utils import load_questions, save_questions

   # Load questions from file
   questions = load_questions()
   
   # Save questions to file
   success = save_questions(questions)

Text Utilities
~~~~~~~~~~~~~

**File**: ``utils/text_utils.py``

Handles text processing and cleaning operations:

- ``clean_question_text()``: Remove unwanted HTML tags from question text
- ``clean_html_for_vector_store()``: Clean HTML for vector store processing
- ``clean_answer_feedback()``: Clean and format answer feedback text
- ``get_all_existing_tags()``: Extract all unique tags from questions
- ``extract_topic_from_text()``: Extract topic from text content

**Usage**:

.. code-block:: python

   from question_app.utils import clean_question_text, extract_topic_from_text

   # Clean question text
   clean_text = clean_question_text("<script>alert('test')</script>What is 2+2?")
   
   # Extract topic
   topic = extract_topic_from_text("Solve the quadratic equation x² + 5x + 6 = 0")

API Package
-----------

**File**: ``api/canvas.py``

The Canvas API module contains all Canvas LMS integration endpoints and utilities:

- Canvas course and quiz management
- Question fetching from Canvas API
- Configuration management
- Canvas API request utilities

**Key Functions**:
- ``fetch_courses()``: Fetch courses from Canvas LMS
- ``fetch_quizzes(course_id)``: Fetch quizzes for a specific course
- ``fetch_all_questions()``: Fetch all questions from a Canvas quiz
- ``make_canvas_request()``: Make Canvas API requests with retry logic
- ``clean_question_text()``: Clean HTML tags from question text

**Endpoints**:
- `GET /api/courses` - Get all available courses
- `GET /api/courses/{course_id}/quizzes` - Get all quizzes for a specific course
- `POST /api/configuration` - Update course and quiz configuration
- `POST /api/fetch-questions` - Fetch questions from Canvas API

**Usage**:

.. code-block:: python

   from question_app.api.canvas import router as canvas_router
   
   # Include in FastAPI app
   app.include_router(canvas_router)

Main Application
---------------

**File**: ``main.py``

The main application file contains:

- FastAPI application setup and configuration
- Router integration and orchestration
- Web interface endpoints
- Imports and re-exports from organized modules

**Key Responsibilities**:

- Application initialization and configuration
- Route definitions and request handling
- Integration of models and utilities
- External service coordination

Import Strategy
--------------

The application uses a facade pattern where ``main.py`` imports from organized modules and re-exports them. This provides:

- **Backward Compatibility**: Existing imports continue to work
- **Clean Interface**: Single import point for external consumers
- **Flexibility**: Easy to refactor internal organization

**Example**:

.. code-block:: python

   # External code can still import from main
   from question_app.main import Question, load_questions, clean_question_text
   
   # Internal organization is hidden
   # Functions are actually imported from utils and models packages

Future Modules
-------------

The following modules are planned for future development:

Additional API Modules
~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Further organize API endpoints by functionality
**Planned Structure**:
- ``api/questions.py``: Question management endpoints
- ``api/chat.py``: Chat assistant endpoints
- ``api/ai.py``: AI feedback generation endpoints
- ``api/objectives.py``: Learning objectives endpoints
- ``api/canvas.py``: Canvas integration endpoints
- ``api/system.py``: System configuration endpoints

Core Package
~~~~~~~~~~~

**Purpose**: Application core configuration and setup
**Planned Structure**:
- ``core/config.py``: Configuration management
- ``core/database.py``: Database connections
- ``core/logging.py``: Logging configuration
- ``core/app.py``: Application initialization

Services Package
~~~~~~~~~~~~~~~

**Purpose**: Business logic and external service integrations
**Planned Structure**:
- ``services/canvas_service.py``: Canvas LMS integration
- ``services/ai_service.py``: AI service integration
- ``services/embedding_service.py``: Embedding generation
- ``services/vector_service.py``: Vector store operations

Benefits of Modular Organization
-------------------------------

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to find and modify specific functionality
3. **Testability**: Isolated components for better testing
4. **Scalability**: Clear structure for adding new features
5. **Team Development**: Multiple developers can work on different modules
6. **Code Reuse**: Utility functions can be imported where needed
7. **Documentation**: Clear organization makes documentation easier
