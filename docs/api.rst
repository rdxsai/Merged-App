API Reference
=============

This document provides detailed information about the Canvas Quiz Manager API endpoints.

Module Organization
------------------

The application is organized into focused modules for better maintainability:

**API Modules** (`src/question_app/api/`)
   - ``canvas.py``: Canvas LMS integration endpoints and utilities
   - ``questions.py``: Question CRUD operations and endpoints
   - Additional API modules can be added for other functionality

**Models** (`src/question_app/models/`)
   - ``question.py``: Question and answer data models
   - ``objective.py``: Learning objective data models

**Utilities** (`src/question_app/utils/`)
   - ``file_utils.py``: File I/O operations for data persistence
   - ``text_utils.py``: Text processing and cleaning functions

**Main Application** (`src/question_app/main.py`)
   - FastAPI application setup and configuration
   - Router integration and orchestration
   - Web interface endpoints

**Services** (`src/question_app/services/`)
   - ``ai_service.py``: AI feedback generation and Azure OpenAI integration

Authentication
--------------

The application uses Canvas API tokens for authentication. Set the `CANVAS_API_TOKEN` environment variable with your Canvas API token.

Base URL
--------

All API endpoints are relative to the base URL: `http://localhost:8080`

Web Interface Endpoints
----------------------

The application provides a comprehensive web interface for managing Canvas quiz questions,
AI feedback generation, and learning objectives. All endpoints return HTML responses
for the web interface unless otherwise specified.

Home Page
~~~~~~~~~

.. http:get:: /

   Display the main application page with all questions.

   **Response:** HTML page with questions table, search functionality, and management tools

   **Features:**
   - View all questions in a paginated table
   - Search and filter questions
   - Quick access to question editing
   - AI feedback generation controls
   - Canvas integration status

Question Management
~~~~~~~~~~~~~~~~~~

The question management endpoints provide full CRUD operations for quiz questions,
including editing, creating, updating, and deleting questions.

.. http:get:: /questions/{question_id}

   Display the question edit page.

   :param question_id: ID of the question to edit
   :type question_id: integer

   **Response:** HTML page with question edit form

   **Features:**
   - Edit question text and HTML content
   - Modify answer options and correct answers
   - Update question metadata (points, type, position)
   - Preview question formatting
   - Save changes with validation

.. http:get:: /questions/new

   Display the new question creation page.

   **Response:** HTML page with new question form

.. http:put:: /questions/{question_id}

   Update an existing question.

   :param question_id: ID of the question to update
   :type question_id: integer

   **Request Body:** QuestionUpdate model
   **Response:** JSON with success status

.. http:post:: /questions/new

   Create a new question.

   **Request Body:** QuestionUpdate model
   **Response:** JSON with success status and question ID

.. http:delete:: /questions/{question_id}

   Delete a question.

   :param question_id: ID of the question to delete
   :type question_id: integer

   **Response:** JSON with success status

Canvas Integration
~~~~~~~~~~~~~~~~~

The Canvas integration endpoints are organized in the Canvas API module for better maintainability.

.. http:post:: /api/fetch-questions

   Fetch all questions from Canvas API.

   **Response:** JSON with success status and count

.. http:get:: /api/courses

   Get all available courses.

   **Response:** JSON with courses list

.. http:get:: /api/courses/{course_id}/quizzes

   Get all quizzes for a specific course.

   :param course_id: Canvas course ID
   :type course_id: string

   **Response:** JSON with quizzes list

.. http:post:: /api/configuration

   Update course and quiz configuration.

   **Request Body:** JSON with course_id and quiz_id
   **Response:** JSON with success status

AI Feedback Generation
~~~~~~~~~~~~~~~~~~~~~

The AI feedback generation system uses Azure OpenAI to provide educational feedback
for quiz questions, helping instructors improve question quality and student learning.

.. http:post:: /questions/{question_id}/generate-feedback

   Generate AI feedback for a question.

   :param question_id: ID of the question
   :type question_id: integer

   **Response:** JSON with generated feedback

   **Features:**
   - AI-powered educational feedback generation
   - Customizable system prompts for feedback style
   - Integration with Azure OpenAI services
   - Feedback quality assessment
   - Batch feedback generation for multiple questions

System Prompt Management
~~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /system-prompt

   Display system prompt edit page.

   **Response:** HTML page with prompt editor

.. http:get:: /system-prompt/api

   Get current system prompt as JSON.

   **Response:** JSON with prompt text

.. http:post:: /system-prompt

   Save system prompt.

   **Request Body:** Form data with prompt text
   **Response:** JSON with success status

Vector Store Management
~~~~~~~~~~~~~~~~~~~~~~

The vector store management system uses ChromaDB to create and maintain semantic
search capabilities for the question database, enabling intelligent retrieval
and RAG functionality.

.. http:post:: /chat/create-vector-store

   Create ChromaDB vector store from questions.

   **Response:** JSON with creation status and statistics

   **Features:**
   - ChromaDB vector database integration
   - Semantic embedding generation using Ollama
   - Automatic vector store creation from questions
   - Search statistics and performance metrics
   - Vector store maintenance and updates

Chat Assistant
~~~~~~~~~~~~~~

The chat assistant provides an intelligent interface for querying the question database
using RAG (Retrieval-Augmented Generation) technology, combining vector search with
AI-powered responses.

.. http:get:: /chat/

   Display chat assistant page.

   **Response:** HTML page with chat interface

   **Features:**
   - Interactive chat interface
   - RAG-powered question retrieval
   - Semantic search across question database
   - AI-generated responses with context
   - Customizable system prompts
   - Welcome message customization

.. http:post:: /chat/message

   Process chat message with RAG.

   **Request Body:** JSON with message and max_chunks
   **Response:** JSON with AI response and retrieved chunks

.. http:get:: /chat/system-prompt

   Display chat system prompt edit page.

   **Response:** HTML page with prompt editor

.. http:post:: /chat/system-prompt

   Save chat system prompt.

   **Request Body:** Form data with prompt text
   **Response:** JSON with success status

.. http:get:: /chat/system-prompt/default

   Get default chat system prompt.

   **Response:** JSON with default prompt

.. http:get:: /chat/welcome-message

   Get current chat welcome message.

   **Response:** JSON with welcome message

.. http:post:: /chat/welcome-message

   Save chat welcome message.

   **Request Body:** JSON or form data with message
   **Response:** JSON with success status

.. http:get:: /chat/welcome-message/default

   Get default chat welcome message.

   **Response:** JSON with default message

Learning Objectives
~~~~~~~~~~~~~~~~~~

The learning objectives management system allows instructors to define, organize,
and track learning objectives for their courses, providing a structured approach
to curriculum design and assessment alignment.

.. http:get:: /objectives

   Display learning objectives management page.

   **Response:** HTML page with objectives editor

   **Features:**
   - Create and edit learning objectives
   - Organize objectives by categories
   - Set priority levels for objectives
   - Track objective creation and updates
   - Export objectives for curriculum planning

.. http:post:: /objectives

   Save learning objectives.

   **Request Body:** ObjectivesUpdate model
   **Response:** JSON with success status

Debug and Testing
~~~~~~~~~~~~~~~~~

.. http:get:: /debug/config

   Get configuration status.

   **Response:** JSON with configuration details

.. http:get:: /debug/ollama-test

   Test Ollama connection.

   **Response:** JSON with connection status

.. http:get:: /debug/question/{question_id}

   Debug information for a specific question.

   :param question_id: ID of the question
   :type question_id: integer

   **Response:** JSON with question debug info

.. http:get:: /test-system-prompt

   Display system prompt testing page.

   **Response:** HTML page with prompt tester

Data Models
-----------

The data models are organized in the ``src/question_app/models/`` package:

**Question Models** (`models/question.py`)
   - ``Answer``: Quiz answer option model
   - ``Question``: Complete quiz question model
   - ``QuestionUpdate``: Model for updating questions
   - ``NewQuestion``: Model for creating new questions

**Objective Models** (`models/objective.py`)
   - ``LearningObjective``: Learning objective model
   - ``ObjectivesUpdate``: Model for updating objectives

Answer
~~~~~~

.. code-block:: python

   class Answer(BaseModel):
       """Pydantic model representing a quiz answer option."""
       
       id: int
       """Unique identifier for the answer"""
       
       text: str
       """The answer text content"""
       
       html: str
       """HTML formatted version of the answer text"""
       
       comments: str
       """Feedback comments for this answer"""
       
       comments_html: str
       """HTML formatted version of the comments"""
       
       weight: float
       """Weight/score for this answer (0-100)"""

Question
~~~~~~~~

.. code-block:: python

   class Question(BaseModel):
       """Pydantic model representing a complete quiz question."""
       
       id: int
       """Unique identifier for the question"""
       
       quiz_id: int
       """ID of the quiz this question belongs to"""
       
       question_name: str
       """Name/title of the question"""
       
       question_type: str
       """Type of question (e.g., 'multiple_choice_question')"""
       
       question_text: str
       """The main question text"""
       
       points_possible: float
       """Maximum points for this question"""
       
       correct_comments: str
       """Feedback shown when answer is correct"""
       
       incorrect_comments: str
       """Feedback shown when answer is incorrect"""
       
       neutral_comments: str
       """General feedback for the question"""
       
       correct_comments_html: str
       """HTML formatted correct comments"""
       
       incorrect_comments_html: str
       """HTML formatted incorrect comments"""
       
       neutral_comments_html: str
       """HTML formatted neutral comments"""
       
       answers: List[Answer]
       """List of answer options for this question"""

QuestionUpdate
~~~~~~~~~~~~~

.. code-block:: python

   class QuestionUpdate(BaseModel):
       """Pydantic model for updating question data."""
       
       question_text: str
       """The updated question text content"""
       
       question_html: str
       """HTML formatted version of the updated question text"""
       
       points_possible: float
       """Updated maximum points possible for this question"""
       
       question_type: str
       """Updated type of question"""
       
       position: int
       """Updated position of the question in the quiz"""

LearningObjective
~~~~~~~~~~~~~~~~

.. code-block:: python

   class LearningObjective(BaseModel):
       """Pydantic model representing a learning objective."""
       
       id: int
       """Unique identifier for the learning objective"""
       
       text: str
       """The learning objective text content"""
       
       description: Optional[str] = None
       """Optional description of the learning objective"""
       
       category: Optional[str] = None
       """Optional category for organizing objectives"""
       
       priority: Optional[int] = None
       """Optional priority level (1-5, where 1 is highest)"""
       
       created_at: Optional[str] = None
       """Timestamp when the objective was created"""
       
       updated_at: Optional[str] = None
       """Timestamp when the objective was last updated"""

ObjectivesUpdate
~~~~~~~~~~~~~~~

.. code-block:: python

   class ObjectivesUpdate(BaseModel):
       """Pydantic model for updating learning objectives."""
       
       objectives: List[LearningObjective]
       """List of learning objectives to update"""

NewQuestion
~~~~~~~~~~

.. code-block:: python

   class NewQuestion(BaseModel):
       """Pydantic model for creating a new question."""
       
       question_text: str
       """The question text content"""
       
       question_html: str
       """HTML formatted version of the question text"""
       
       points_possible: float
       """Maximum points possible for this question"""
       
       question_type: str
       """Type of question (e.g., 'multiple_choice_question')"""
       
       position: int
       """Position of the question in the quiz"""
       
       quiz_id: int
       """ID of the quiz this question belongs to"""
       
       course_id: int
       """ID of the course this question belongs to"""

Utility Functions
----------------

The application provides utility functions organized in the ``src/question_app/utils/`` package:

**File Utilities** (`utils/file_utils.py`)
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

**Text Utilities** (`utils/text_utils.py`)
   - ``clean_question_text()``: Remove unwanted HTML tags from question text
   - ``clean_html_for_vector_store()``: Clean HTML for vector store processing
   - ``clean_answer_feedback()``: Clean and format answer feedback text
   - ``get_all_existing_tags()``: Extract all unique tags from questions
   - ``extract_topic_from_text()``: Extract topic from text content

Error Responses
--------------

The API uses standard HTTP status codes and returns error details in JSON format:

.. code-block:: json

   {
     "detail": "Error message description"
   }

Common Status Codes
~~~~~~~~~~~~~~~~~~

* **200 OK**: Request successful
* **400 Bad Request**: Invalid request data
* **404 Not Found**: Resource not found
* **500 Internal Server Error**: Server error
* **503 Service Unavailable**: External service unavailable
