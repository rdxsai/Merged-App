# Changelog

## [Unreleased] - API Restructuring and Modularization

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
  - Organized chat endpoints, vector store operations, and embedding generation
  - Added comprehensive chat interface with semantic search capabilities
  - Included chat system prompt and welcome message management
  - Maintained vector store creation and search functionality
  - Added Ollama embedding integration for local AI processing

- **AI Service Module** (`src/question_app/services/ai_service.py`)
  - Extracted AI feedback generation logic from main.py
  - Separated AI business logic from API endpoints
  - Eliminated circular import issues
  - Added comprehensive error handling and logging

### Changed

- **API Endpoint Paths**:
  - `/fetch-questions` → `/api/fetch-questions`
  - Canvas endpoints now use `/api/*` prefix for consistency
  - Question endpoints maintain original paths for backward compatibility
  - Chat endpoints now use `/chat/*` prefix for consistency
- **Frontend Updates**:
  - Updated `templates/index.html` to use new `/api/fetch-questions` endpoint
- **Test Updates**:
  - Updated test files to patch functions in `question_app.api.canvas` instead of `question_app.main`
  - Updated test files to patch functions in `question_app.api.questions` instead of `question_app.main`
  - Updated test files to patch functions in `question_app.api.chat` instead of `question_app.main`
  - Fixed import paths for Canvas-related and question-related functions
  - Fixed AI service mocking to target correct import paths

### Updated Documentation

- **README.md**: Added API structure section and updated project structure
- **docs/api.rst**: Updated module organization and endpoint documentation
- **docs/modules.rst**: Added API package and Services package documentation
- **docs/api_structure.md**: Updated with Questions API and AI Service information

### Architecture Improvements

- **Modularity**: Functionality is now isolated in focused modules
- **Maintainability**: Easier to maintain and update specific functionality
- **Testability**: API modules can be tested independently
- **Scalability**: Easy to add more API modules for other functionality
- **Separation of Concerns**: Clear boundaries between different types of functionality
- **Backward Compatibility**: All existing functionality preserved

### Technical Details

- **Router Integration**: Both Canvas and Questions API routers are automatically included in main FastAPI app
- **Function Organization**: Canvas-related and question-related functions moved from main.py to dedicated modules
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
  - `question_app.services.ai_service` for AI functionality
- **Documentation**: Refer to `docs/api_structure.md` for detailed API documentation
