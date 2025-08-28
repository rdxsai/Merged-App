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
   │   ├── canvas.py            # Canvas LMS integration endpoints
   │   ├── questions.py         # Question CRUD operations and endpoints
   │   ├── chat.py              # RAG-based chat functionality
   │   ├── vector_store.py      # Vector store operations and semantic search
   │   ├── system_prompt.py     # System prompt management endpoints
   │   └── debug.py             # Debugging and testing endpoints
   ├── models/                  # Data models and schemas
   │   ├── __init__.py
   │   ├── question.py          # Question-related models
   │   └── objective.py         # Learning objective models
   ├── utils/                   # Utility functions
   │   ├── __init__.py
   │   ├── file_utils.py        # File I/O operations
   │   └── text_utils.py        # Text processing utilities
   ├── services/                # Business logic services
   │   ├── __init__.py          # Services package initialization
   │   └── ai_service.py        # AI feedback generation and Azure OpenAI integration
   └── core/                    # Core configuration and app setup
       ├── __init__.py          # Core module exports
       ├── config.py            # Centralized configuration management
       ├── logging.py           # Centralized logging setup
       └── app.py               # FastAPI application setup

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

The API package contains organized endpoint modules for different functionality.

Canvas API
~~~~~~~~~~

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

Questions API
~~~~~~~~~~~~

**File**: ``api/questions.py``

The Questions API module contains all question-related CRUD operations and endpoints:

- Question creation, reading, updating, and deletion
- HTML template rendering for web interface
- AI feedback generation integration
- Proper error handling and logging

**Endpoints**:
- `DELETE /questions/{question_id}` - Delete a question
- `GET /questions/new` - Show new question creation page
- `POST /questions/new` - Create a new question
- `GET /questions/{question_id}` - Show question edit page
- `PUT /questions/{question_id}` - Update a question
- `POST /questions/{question_id}/generate-feedback` - Generate AI feedback for a question

**Usage**:

.. code-block:: python

   from question_app.api.questions import router as questions_router
   
   # Include in FastAPI app
   app.include_router(questions_router)

Chat API
~~~~~~~~

**File**: ``api/chat.py``

The Chat API module contains all RAG-based chat functionality:

- RAG-based chat interface with semantic search
- Chat system prompt and welcome message management
- Integration with vector store for semantic search
- Comprehensive error handling and logging

**Key Functions**:
- ``load_chat_system_prompt()``: Load chat system prompt
- ``save_chat_system_prompt()``: Save chat system prompt
- ``load_welcome_message()``: Load welcome message
- ``save_welcome_message()``: Save welcome message

**Endpoints**:
- `GET /chat/` - Chat interface page
- `POST /chat/message` - Process chat messages with RAG

- `GET /chat/system-prompt` - Chat system prompt edit page
- `POST /chat/system-prompt` - Save chat system prompt
- `GET /chat/system-prompt/default` - Get default chat system prompt
- `GET /chat/welcome-message` - Get chat welcome message
- `POST /chat/welcome-message` - Save chat welcome message
- `GET /chat/welcome-message/default` - Get default welcome message

**Usage**:

.. code-block:: python

   from question_app.api.chat import router as chat_router
   
   # Include in FastAPI app
   app.include_router(chat_router)

Vector Store API
~~~~~~~~~~~~~~~

**File**: ``api/vector_store.py``

The Vector Store API module contains all vector store operations and semantic search functionality:

- Vector store creation and management using ChromaDB
- Ollama embedding integration for local AI processing
- Semantic search capabilities
- Document chunking and processing
- Vector store status monitoring

**Key Functions**:
- ``get_ollama_embeddings()``: Generate embeddings using Ollama
- ``create_comprehensive_chunks()``: Create text chunks for vector store
- ``search_vector_store()``: Search vector store for similar content

**Endpoints**:
- `POST /vector-store/create` - Create ChromaDB vector store from questions
- `GET /vector-store/search` - Search vector store for relevant content
- `GET /vector-store/status` - Get vector store status
- `DELETE /vector-store/` - Delete vector store

**Usage**:

.. code-block:: python

   from question_app.api.vector_store import router as vector_store_router
   
   # Include in FastAPI app
   app.include_router(vector_store_router)

Services Package
---------------

The Services package contains business logic services separated from API endpoints.

AI Service
~~~~~~~~~~

**File**: ``services/ai_service.py``

The AI Service module contains AI-related business logic:

- Azure OpenAI integration for feedback generation
- AI response parsing and formatting
- Comprehensive error handling
- Token usage tracking

**Key Functions**:
- ``generate_feedback_with_ai()``: Generate educational feedback using Azure OpenAI

**Features**:
- Azure OpenAI API integration
- Structured feedback parsing
- Error handling and retry logic
- Token usage statistics

**Usage**:

.. code-block:: python

   from question_app.services.ai_service import generate_feedback_with_ai
   
   # Generate feedback for a question
   feedback = await generate_feedback_with_ai(question_data, system_prompt)

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
- ``api/questions.py``: Question management endpoints (✅ Implemented)
- ``api/chat.py``: Chat assistant endpoints (✅ Implemented)
- ``api/ai.py``: AI feedback generation endpoints
- ``api/objectives.py``: Learning objectives endpoints (✅ Implemented)
- ``api/canvas.py``: Canvas integration endpoints (✅ Implemented)
- ``api/system_prompt.py``: System prompt management endpoints (✅ Implemented)

Core Package
~~~~~~~~~~~

**Purpose**: Application core configuration and setup
**Implemented Structure**:
- ``core/config.py``: Centralized configuration management ✅
- ``core/logging.py``: Centralized logging configuration ✅
- ``core/app.py``: FastAPI application setup ✅
- ``core/__init__.py``: Core module exports ✅

**Key Features**:
- Centralized environment variable management
- Configuration validation and error reporting
- Consistent logging across the application
- Clean application initialization and setup

See :doc:`core_modules` for detailed documentation.

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
