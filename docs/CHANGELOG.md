# Changelog

## [Unreleased] - API Restructuring and Modularization

### Added

- **Vector Store API Module** (`src/question_app/api/vector_store.py`)

  - Extracted vector store operations from chat.py into dedicated module
  - Organized vector store functionality into focused module
  - Added vector store creation, search, status, and deletion endpoints
  - Moved embedding generation and document chunking functions
  - Added comprehensive error handling and logging
  - Maintained backward compatibility with chat functionality

- **System Prompt API Module** (`src/question_app/api/system_prompt.py`)

  - Extracted system prompt management endpoints from main.py
  - Organized system prompt functionality into dedicated module
  - Added system prompt editing, API access, and test functionality
  - Maintained HTML template rendering for web interface
  - Added proper error handling and logging

### Added

### Added

- **Canvas API Module** (`src/question_app/api/canvas.py`)

  - Extracted Canvas-related endpoints from main.py
  - Organized Canvas functionality into dedicated module
  - Added proper router structure with `/api` prefix
  - Included Canvas API utilities and request handling

- **Questions API Module** (`src/question_app/api/questions.py`)

  - Extracted question CRUD endpoints from main.py
  - Organized question management functionality into dedicated module
  - Added full CRUD operations for questions
  - Included AI feedback generation integration
  - Maintained HTML template rendering for web interface

- **Chat API Module** (`src/question_app/api/chat.py`)

  - Extracted RAG-based chat functionality from main.py
  - Organized chat endpoints and chat-specific operations
  - Added comprehensive chat interface with semantic search capabilities
  - Included chat system prompt and welcome message management
  - Integrated with vector store module for semantic search functionality
  - Maintained backward compatibility with existing chat features

- **AI Service Module** (`src/question_app/services/ai_service.py`)

  - Extracted AI feedback generation logic from main.py
  - Separated AI business logic from API endpoints
  - Eliminated circular import issues
  - Added comprehensive error handling and logging

- **Objectives API Module** (`src/question_app/api/objectives.py`)
  - Extracted learning objectives management endpoints from main.py
  - Organized objectives functionality into dedicated module
  - Added objectives viewing and saving endpoints
  - Maintained HTML template rendering for web interface
  - Added proper error handling and logging

### Changed

- **API Endpoint Paths**:
  - `/fetch-questions` → `/api/fetch-questions`
  - Canvas endpoints now use `/api/*` prefix for consistency
  - Question endpoints maintain original paths for backward compatibility
  - Chat endpoints now use `/chat/*` prefix for consistency
  - Vector store endpoints now use `/vector-store/*` prefix for consistency
  - System prompt endpoints now use `/system-prompt/*` prefix for consistency
  - Objectives endpoints now use `/objectives/*` prefix for consistency
- **Frontend Updates**:
  - Updated `templates/index.html` to use new `/api/fetch-questions` endpoint
- **Test Updates**:
  - Updated test files to patch functions in `question_app.api.canvas` instead of `question_app.main`
  - Updated test files to patch functions in `question_app.api.questions` instead of `question_app.main`
  - Updated test files to patch functions in `question_app.api.chat` instead of `question_app.main`
  - Updated test files to patch functions in `question_app.api.vector_store` instead of `question_app.api.chat`
  - Updated test files to patch functions in `question_app.api.system_prompt` instead of `question_app.main`
  - Updated test files to patch functions in `question_app.api.objectives` instead of `question_app.main`
  - Fixed import paths for Canvas-related, question-related, vector store, system prompt, and objectives functions
  - Fixed AI service mocking to target correct import paths
  - Updated test expectations for vector store error handling behavior

### Updated Documentation

- **README.md**: Added API structure section and updated project structure
- **docs/api.rst**: Updated module organization and endpoint documentation
- **docs/modules.rst**: Added API package and Services package documentation
- **docs/api_structure.md**: Updated with Vector Store API, Questions API, System Prompt API, and AI Service information
- **docs/CHANGELOG.md**: Added vector store refactoring documentation

### Architecture Improvements

- **Modularity**: Functionality is now isolated in focused modules
- **Maintainability**: Easier to maintain and update specific functionality
- **Testability**: API modules can be tested independently
- **Scalability**: Easy to add more API modules for other functionality
- **Separation of Concerns**: Clear boundaries between different types of functionality
- **Backward Compatibility**: All existing functionality preserved

### Technical Details

- **Router Integration**: Canvas, Questions, Chat, Vector Store, and System Prompt API routers are automatically included in main FastAPI app
- **Function Organization**: Canvas-related, question-related, vector store, and system prompt functions moved from main.py to dedicated modules
- **Import Structure**: Clean separation between API modules, services, and main application
- **Error Handling**: Maintained consistent error handling across all endpoints
- **Service Layer**: Introduced services package for business logic separation

### Migration Notes

- **Frontend**: Update any hardcoded `/fetch-questions` calls to `/api/fetch-questions`
- **API Consumers**: Canvas endpoints now use `/api/*` prefix, chat endpoints use `/chat/*` prefix
- **Testing**: Update test patches to use appropriate modules:
  - `question_app.api.canvas` for Canvas functionality
  - `question_app.api.questions` for question functionality
  - `question_app.api.chat` for chat and vector store functionality
  - `question_app.api.system_prompt` for system prompt functionality
  - `question_app.api.objectives` for objectives functionality
  - `question_app.services.ai_service` for AI functionality
- **Documentation**: Refer to `docs/api_structure.md` for detailed API documentation
