# API Structure Documentation

## Overview

The Question App API has been restructured to organize endpoints by functionality. Both Canvas-related and question-related endpoints have been extracted into dedicated modules for better maintainability and separation of concerns.

## Recent Improvements (v0.3.0)

### Type Safety Enhancements
- **100% Pyright Compliance**: All type checking errors resolved
- **80% Mypy Improvement**: Reduced from 15 to 3 errors
- **Enhanced Error Handling**: Proper HTTPException types throughout
- **Type Guards**: Runtime type checking for complex scenarios
- **Comprehensive Annotations**: Full type coverage across all modules

### Development Experience
- **VS Code Integration**: Complete development environment setup
- **Debugging Support**: Full debugging for FastAPI and tests
- **Task Automation**: Pre-configured development tasks
- **Real-time Type Checking**: Integrated type checking in VS Code

### Bug Fixes
- **Feedback Generation**: Fixed new question feedback generation workflow
- **Environment Configuration**: Improved PYTHONPATH and module discovery
- **API Compatibility**: Enhanced type compatibility across endpoints

## API Modules

### Canvas API (`src/question_app/api/canvas.py`)

Contains all Canvas LMS integration endpoints and utilities:

#### Endpoints:

- `GET /api/courses` - Get all available courses
- `GET /api/courses/{course_id}/quizzes` - Get all quizzes for a specific course
- `POST /api/configuration` - Update course and quiz configuration
- `POST /api/fetch-questions` - Fetch questions from Canvas API

#### Functions:

- `fetch_courses()` - Fetch courses from Canvas LMS
- `fetch_quizzes(course_id)` - Fetch quizzes for a specific course
- `fetch_all_questions()` - Fetch all questions from a Canvas quiz
- `make_canvas_request()` - Make Canvas API requests with retry logic
- `clean_question_text()` - Clean HTML tags from question text

#### Models:

- `ConfigurationUpdate` - Model for configuration update requests
- `FetchQuestionsResponse` - Model for fetch questions response

### Questions API (`src/question_app/api/questions.py`)

Contains all question-related CRUD operations and endpoints:

#### Endpoints:

- `DELETE /questions/{question_id}` - Delete a question
- `GET /questions/new` - Show new question creation page
- `POST /questions/new` - Create a new question
- `GET /questions/{question_id}` - Show question edit page
- `PUT /questions/{question_id}` - Update a question
- `POST /questions/{question_id}/generate-feedback` - Generate AI feedback for a question

#### Features:

- Full CRUD operations for questions
- HTML template rendering for web interface
- AI feedback generation integration with automatic question saving for new questions
- Proper error handling and logging
- Backward compatibility with existing data structure
- Enhanced JavaScript workflow for new question feedback generation

### System Prompt API (`src/question_app/api/system_prompt.py`)

Contains all system prompt management functionality:

#### Endpoints:

- `GET /system-prompt/` - System prompt edit page
- `GET /system-prompt/api` - Get current system prompt as JSON
- `POST /system-prompt/` - Save system prompt
- `GET /system-prompt/test` - Test system prompt functionality page

#### Functions:

- `load_system_prompt()` - Load system prompt from file
- `save_system_prompt()` - Save system prompt to file

#### Features:

- System prompt editing interface
- API access to system prompt
- Test functionality for system prompts
- Proper error handling and logging
- HTML template rendering for web interface

### Objectives API (`src/question_app/api/objectives.py`)

Contains all learning objectives management functionality:

#### Endpoints:

- `GET /objectives/` - Learning objectives management page
- `POST /objectives/` - Save learning objectives

#### Functions:

- `load_objectives()` - Load learning objectives from file
- `save_objectives()` - Save learning objectives to file

#### Features:

- Learning objectives management interface
- JSON API for saving objectives
- Proper error handling and logging
- HTML template rendering for web interface

### Chat API (`src/question_app/api/chat.py`)

Contains all RAG-based chat functionality:

#### Endpoints:

- `GET /chat/` - Chat interface page
- `POST /chat/message` - Process chat messages with RAG
- `GET /chat/system-prompt` - Chat system prompt edit page
- `POST /chat/system-prompt` - Save chat system prompt
- `GET /chat/system-prompt/default` - Get default chat system prompt
- `GET /chat/welcome-message` - Get chat welcome message
- `POST /chat/welcome-message` - Save chat welcome message
- `GET /chat/welcome-message/default` - Get default welcome message

#### Functions:

- `load_chat_system_prompt()` - Load chat system prompt
- `save_chat_system_prompt()` - Save chat system prompt
- `load_welcome_message()` - Load welcome message
- `save_welcome_message()` - Save welcome message

#### Features:

- RAG-based chat interface with semantic search
- Chat system prompt and welcome message management
- Comprehensive error handling and logging
- HTML template rendering for web interface
- Integration with vector store for semantic search

### Vector Store API (`src/question_app/api/vector_store.py`)

Contains all vector store operations and semantic search functionality:

#### Endpoints:

- `POST /vector-store/create` - Create ChromaDB vector store from questions
- `GET /vector-store/search` - Search vector store for relevant content
- `GET /vector-store/status` - Get vector store status
- `DELETE /vector-store/` - Delete vector store

#### Functions:

- `get_ollama_embeddings()` - Generate embeddings using Ollama
- `create_comprehensive_chunks()` - Create text chunks for vector store
- `search_vector_store()` - Search vector store for similar content

#### Features:

- Vector store creation and management using ChromaDB
- Ollama embedding integration for local AI processing
- Semantic search capabilities
- Comprehensive error handling and logging
- Document chunking and processing
- Vector store status monitoring

### Debug API (`src/question_app/api/debug.py`)

Contains all debugging and testing functionality:

#### Endpoints:

- `GET /debug/question/{question_id}` - Inspect specific question details
- `GET /debug/config` - Check application configuration status
- `GET /debug/ollama-test` - Test Ollama connection and model availability

#### Features:

- Question inspection and debugging
- Configuration validation and status reporting
- Ollama service connectivity testing
- Comprehensive error reporting and troubleshooting
- Development and testing support

## Services

### AI Service (`src/question_app/services/ai_service.py`)

Contains AI-related business logic:

#### Functions:

- `generate_feedback_with_ai()` - AI feedback generation using Azure OpenAI

#### Features:

- Azure OpenAI integration
- Feedback generation logic
- Response parsing and formatting
- Comprehensive error handling

## Integration

The API routers are automatically included in the main FastAPI application:

```python
from .api import canvas_router, questions_router, chat_router, vector_store_router, system_prompt_router, objectives_router, debug_router
app.include_router(canvas_router)
app.include_router(questions_router)
app.include_router(chat_router)
app.include_router(vector_store_router)
app.include_router(system_prompt_router)
app.include_router(objectives_router)
app.include_router(debug_router)
```

## Benefits

1. **Modularity**: Functionality is isolated in focused modules
2. **Maintainability**: Easier to maintain and update specific functionality
3. **Testability**: API modules can be tested independently
4. **Scalability**: Easy to add more API modules for other functionality
5. **Documentation**: Better organization makes the API easier to understand
6. **Separation of Concerns**: Clear boundaries between different types of functionality

## Future Extensions

Additional API modules can be created for:

- System configuration
- User authentication and authorization
- Additional AI integrations
- Analytics and reporting
- Additional Canvas integrations

## Usage

The API endpoints maintain the same interface as before, so existing frontend code and integrations will continue to work without changes.
