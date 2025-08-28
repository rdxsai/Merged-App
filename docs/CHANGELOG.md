# Changelog

## [Unreleased] - API Restructuring

### Added

- **Canvas API Module** (`src/question_app/api/canvas.py`)
  - Extracted Canvas-related endpoints from main.py
  - Organized Canvas functionality into dedicated module
  - Added proper router structure with `/api` prefix
  - Included Canvas API utilities and request handling

### Changed

- **API Endpoint Paths**:
  - `/fetch-questions` → `/api/fetch-questions`
  - Canvas endpoints now use `/api/*` prefix for consistency
- **Frontend Updates**:
  - Updated `templates/index.html` to use new `/api/fetch-questions` endpoint
- **Test Updates**:
  - Updated test files to patch functions in `question_app.api.canvas` instead of `question_app.main`
  - Fixed import paths for Canvas-related functions

### Updated Documentation

- **README.md**: Added API structure section and updated project structure
- **docs/api.rst**: Updated module organization and endpoint documentation
- **docs/modules.rst**: Added API package documentation and updated structure
- **docs/api_structure.md**: Created comprehensive API structure documentation

### Architecture Improvements

- **Modularity**: Canvas functionality is now isolated in its own module
- **Maintainability**: Easier to maintain and update Canvas-specific code
- **Testability**: Canvas endpoints can be tested independently
- **Scalability**: Easy to add more API modules for other functionality
- **Backward Compatibility**: All existing functionality preserved

### Technical Details

- **Router Integration**: Canvas API router is automatically included in main FastAPI app
- **Function Organization**: Canvas-related functions moved from main.py to canvas.py
- **Import Structure**: Clean separation between API modules and main application
- **Error Handling**: Maintained consistent error handling across all endpoints

### Migration Notes

- **Frontend**: Update any hardcoded `/fetch-questions` calls to `/api/fetch-questions`
- **API Consumers**: Canvas endpoints now use `/api/*` prefix
- **Testing**: Update test patches to use `question_app.api.canvas` module
- **Documentation**: Refer to `docs/api_structure.md` for detailed API documentation
