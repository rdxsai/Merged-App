# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-08-28

### Added
- **VS Code Integration**: Comprehensive VS Code configuration for optimal development experience
  - `.vscode/settings.json`: Python interpreter, PYTHONPATH, formatting, testing configuration
  - `.vscode/tasks.json`: Pre-configured tasks for Poetry install, dev server, tests, lint, format, docs
  - `.vscode/launch.json`: Debug configurations for API and tests
  - `.vscode/extensions.json`: Recommended VS Code extensions
- **Enhanced Type Safety**: Comprehensive type checking and validation
  - 100% Pyright compliance (0 errors)
  - 80% Mypy improvement (15 errors → 3 errors)
  - Comprehensive type annotations across all modules
  - Type guards for runtime type checking
  - Proper error handling with typed exceptions
- **Improved Development Workflow**: Streamlined development experience
  - Command Palette integration for common tasks
  - Integrated testing with Test Explorer
  - Real-time type checking and error reporting
  - Automated code formatting and linting

### Fixed
- **Feedback Generation for New Questions**: Fixed issue where new questions couldn't generate AI feedback
  - Automatic question saving before feedback generation
  - Proper question ID tracking and updates
  - Enhanced user feedback messages
  - Validation to ensure question text exists before generating feedback
- **Type Safety Issues**: Resolved multiple type checking errors
  - Canvas API string indexing issues
  - Vector Store embeddings type compatibility
  - Test exception handling with proper HTTPException types
  - UploadFile handling in chat API
  - AI service collection indexing issues
- **Environment Configuration**: Improved environment setup
  - Added PYTHONPATH to .env and .env.template for proper module discovery
  - Configured VS Code to load environment variables for debugging
  - Enhanced module path resolution

### Changed
- **Version Bump**: Updated from v0.2.0 to v0.3.0
- **Documentation Updates**: Enhanced README with VS Code configuration and type safety information
- **Project Structure**: Added VS Code configuration directory to project structure
- **Development Tools**: Integrated comprehensive development tooling

### Technical Details
- **Type Checking Results**:
  - Pyright: 14 errors → 0 errors (100% improvement)
  - Mypy: 15 errors → 3 errors (80% improvement)
  - Remaining mypy errors are known limitations with complex nested logic
- **VS Code Features**:
  - Python interpreter configuration
  - PYTHONPATH setup for src/ layout
  - Integrated debugging for FastAPI and tests
  - Task automation for common development workflows
  - Real-time type checking and error reporting

## [0.2.0] - 2024-12-XX

### Added
- Canvas LMS integration for fetching quiz questions
- AI-powered feedback generation using Azure OpenAI
- RAG-based chat assistant with semantic search
- Vector store operations using ChromaDB
- Learning objectives management
- System prompt customization
- Comprehensive test suite

### Changed
- Initial release with core functionality

## [0.1.0] - 2024-XX-XX

### Added
- Initial project setup
- Basic FastAPI application structure
- Core configuration management
- Basic question management functionality

---

## Development Notes

### Type Safety Standards
This project maintains high standards for type safety:
- **Pyright**: 100% compliance (0 errors)
- **Mypy**: 80% compliance (3 remaining errors are known limitations)
- **Pydantic**: Comprehensive data validation
- **Type Guards**: Runtime type checking where needed

### VS Code Integration
The project includes comprehensive VS Code configuration:
- **Tasks**: Poetry install, dev server, tests, lint, format, docs
- **Debugging**: Full debugging support for FastAPI and tests
- **Extensions**: Recommended extensions for Python development
- **Settings**: Optimized for Poetry projects with src/ layout

### Development Workflow
1. Use VS Code Command Palette for common tasks
2. Leverage integrated debugging for development
3. Run type checking regularly with `poetry run type-check`
4. Use automated formatting with `poetry run format`
5. Run tests with `poetry run test`
