# Development Guide

## Overview

This guide covers development setup, coding standards, and best practices for contributing to the Question App project.

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Git for version control
- VS Code (recommended) with extensions

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd questionapp

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Verify installation
poetry run test
```

### VS Code Configuration

The project includes comprehensive VS Code configuration:

#### Recommended Extensions

- **Python**: Microsoft Python extension
- **Pylance**: Python language server
- **Black Formatter**: Code formatting
- **isort**: Import sorting
- **Prettier**: Code formatting
- **GitLens**: Git integration

#### Workspace Settings

The `.vscode/settings.json` file configures:

- Python interpreter path
- Code formatting rules
- Linting configuration
- Type checking settings

#### Tasks

Pre-configured development tasks in `.vscode/tasks.json`:

- **Build**: Install dependencies
- **Test**: Run test suite
- **Lint**: Run code linting
- **Format**: Format code
- **Type Check**: Run type checking

#### Debugging

Debug configurations for:

- FastAPI application
- Unit tests
- Integration tests

## Project Structure

```
questionapp/
├── src/question_app/
│   ├── api/                 # API endpoints
│   │   ├── canvas.py        # Canvas LMS integration
│   │   ├── chat.py          # Chat functionality
│   │   ├── debug.py         # Debug endpoints
│   │   ├── objectives.py    # Learning objectives
│   │   ├── questions.py     # Question management
│   │   ├── system_prompt.py # System prompts
│   │   └── vector_store.py  # Vector store operations
│   ├── core/                # Core application
│   │   ├── app.py           # FastAPI setup
│   │   ├── config.py        # Configuration management
│   │   └── logging.py       # Logging setup
│   ├── models/              # Pydantic models
│   │   ├── question.py      # Question models
│   │   └── objective.py     # Objective models
│   ├── services/            # Business logic
│   │   └── ai_service.py    # AI integration
│   ├── utils/               # Utility functions
│   │   ├── file_utils.py    # File operations
│   │   └── text_utils.py    # Text processing
│   └── main.py              # Application entry point
├── tests/                   # Test suite
├── templates/               # HTML templates
├── static/                  # Static assets
├── config/                  # Configuration files
├── data/                    # Data files
└── docs/                    # Documentation
```

## Coding Standards

### Python Style Guide

Follow PEP 8 and project-specific conventions:

#### Code Formatting

- Use Black for code formatting
- Line length: 88 characters
- Use 4 spaces for indentation
- No tabs

#### Import Organization

Use isort for import organization:

```python
# Standard library imports
import json
import os
from typing import Dict, List

# Third-party imports
import httpx
from fastapi import APIRouter, HTTPException

# Local imports
from ..core import config, get_logger
from ..models import QuestionUpdate
```

#### Type Hints

Use comprehensive type hints:

```python
from typing import Any, Dict, List, Optional

def process_questions(questions: List[Dict[str, Any]]) -> bool:
    """Process a list of questions."""
    pass

async def fetch_data(url: str, timeout: Optional[float] = None) -> Dict[str, Any]:
    """Fetch data from URL."""
    pass
```

### Documentation Standards

#### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Short description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2, defaults to 0

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong

    Note:
        Additional notes about the function

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True

    See Also:
        :func:`related_function`: Description of related function
    """
    pass
```

#### API Documentation

Document all API endpoints with:

- Clear descriptions
- Request/response examples
- Error scenarios
- Parameter validation

### Error Handling

#### HTTP Exceptions

Use appropriate HTTP status codes:

```python
from fastapi import HTTPException

# Bad request
raise HTTPException(status_code=400, detail="Invalid input")

# Not found
raise HTTPException(status_code=404, detail="Resource not found")

# Server error
raise HTTPException(status_code=500, detail="Internal server error")
```

#### Logging

Use structured logging:

```python
from ..core import get_logger

logger = get_logger(__name__)

logger.info("Operation started", extra={"operation": "fetch_questions"})
logger.error("Operation failed", extra={"error": str(e)})
```

## Development Workflow

### Git Workflow

#### Branch Naming

- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `docs/documentation-update`: Documentation changes
- `refactor/component-name`: Code refactoring

#### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:

- `feat(api): add new question endpoint`
- `fix(canvas): handle rate limiting properly`
- `docs(readme): update installation instructions`

### Development Commands

For detailed tool usage and advanced options, see the [Development Tools Reference](development_tools.rst).

#### Code Quality

```bash
# Format code
poetry run format

# Lint code
poetry run lint

# Type checking
poetry run type-check
```

#### Testing

```bash
# Run all tests
poetry run test

# Run with coverage
poetry run test --coverage

# Run specific test types
poetry run test --type unit
poetry run test --type integration
poetry run test --type ai
poetry run test --type api
```

#### Documentation

```bash
# Build documentation
poetry run docs-simple

# Serve documentation locally
poetry run docs-serve
```

#### Development Server

```bash
# Start development server
poetry run dev

# Start production server
poetry run start
```

### Testing Strategy

#### Unit Tests

Test individual functions and classes:

```python
import pytest
from unittest.mock import Mock, patch

def test_function_name():
    """Test function behavior."""
    # Arrange
    input_data = {"test": "data"}

    # Act
    result = function_name(input_data)

    # Assert
    assert result is True
```

#### Integration Tests

Test API endpoints and external integrations:

```python
from fastapi.testclient import TestClient

def test_api_endpoint(client: TestClient):
    """Test API endpoint."""
    response = client.get("/api/courses")
    assert response.status_code == 200
    assert "courses" in response.json()
```

#### Mocking External Services

Mock external API calls:

```python
@patch('httpx.AsyncClient.get')
async def test_canvas_integration(mock_get):
    """Test Canvas API integration."""
    mock_get.return_value.json.return_value = [{"id": 1, "name": "Test"}]
    mock_get.return_value.raise_for_status.return_value = None

    result = await fetch_courses()
    assert len(result) == 1
```

## API Development

### Adding New Endpoints

#### 1. Create API Module

Create a new file in `src/question_app/api/`:

```python
"""
New API module for the Question App.

This module contains functionality for...
"""

from fastapi import APIRouter, HTTPException
from ..core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/new-feature", tags=["new-feature"])

@router.get("/")
async def get_feature():
    """Get feature information."""
    try:
        # Implementation
        return {"success": True, "data": "feature"}
    except Exception as e:
        logger.error(f"Error in get_feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2. Register Router

Add to `src/question_app/api/__init__.py`:

```python
from .new_feature import router as new_feature_router

__all__ = [
    # ... existing routers
    "new_feature_router",
]
```

#### 3. Include in App

Add to `src/question_app/core/app.py`:

```python
from ..api import new_feature_router

app.include_router(new_feature_router)
```

### Data Models

#### Pydantic Models

Create models in `src/question_app/models/`:

```python
from pydantic import BaseModel
from typing import List, Optional

class NewModel(BaseModel):
    """Model for new feature."""

    id: int
    name: str
    description: Optional[str] = None
    tags: List[str] = []

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Example",
                "description": "Example description",
                "tags": ["tag1", "tag2"]
            }
        }
```

### Error Handling

#### Custom Exceptions

Create custom exceptions for specific error cases:

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

class ServiceUnavailableError(Exception):
    """Raised when external service is unavailable."""
    pass
```

#### Error Response Models

Define consistent error responses:

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str
    error_code: Optional[str] = None
    timestamp: str
```

## Database and Data Management

### File-Based Storage

The application uses file-based storage for simplicity:

#### Data Files

- `data/quiz_questions.json`: Quiz questions
- `data/learning_objectives.json`: Learning objectives
- `config/system_prompt.txt`: System prompts

#### File Operations

Use utility functions for file operations:

```python
from ..utils.file_utils import load_json, save_json

def load_questions() -> List[Dict[str, Any]]:
    """Load questions from file."""
    return load_json("data/quiz_questions.json", default=[])

def save_questions(questions: List[Dict[str, Any]]) -> bool:
    """Save questions to file."""
    return save_json("data/quiz_questions.json", questions)
```

### Data Validation

#### Input Validation

Validate all input data:

```python
from pydantic import ValidationError

def process_question_data(data: Dict[str, Any]) -> QuestionUpdate:
    """Process and validate question data."""
    try:
        return QuestionUpdate(**data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### Data Sanitization

Sanitize data before storage:

```python
def sanitize_text(text: str) -> str:
    """Sanitize text input."""
    # Remove potentially dangerous HTML
    # Normalize whitespace
    # Validate content
    return cleaned_text
```

## Security Considerations

### Input Validation

- Validate all user inputs
- Sanitize HTML content
- Check file uploads
- Validate API parameters

### API Security

- Rate limiting for external APIs
- Error message sanitization
- Secure configuration management
- Input size limits

### Data Protection

- Secure storage of sensitive data
- API key rotation
- Access control implementation
- Audit logging

## Performance Optimization

### Caching

Implement caching for expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(data: str) -> Dict[str, Any]:
    """Cache expensive operations."""
    pass
```

### Async Operations

Use async/await for I/O operations:

```python
async def fetch_data(url: str) -> Dict[str, Any]:
    """Fetch data asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Database Optimization

For future database implementation:

- Use connection pooling
- Implement query optimization
- Add database indexes
- Monitor query performance

## Monitoring and Logging

### Logging Configuration

Configure structured logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        return json.dumps(log_entry)
```

### Application Monitoring

Monitor application health:

```python
@router.get("/health")
async def health_check():
    """Application health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.3.0"
    }
```

### Error Tracking

Track and report errors:

```python
def log_error(error: Exception, context: Dict[str, Any]):
    """Log error with context."""
    logger.error(
        f"Error occurred: {error}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
    )
```

## Deployment Considerations

### Environment Configuration

- Use environment-specific configuration
- Secure sensitive data
- Implement health checks
- Configure logging levels

### Production Setup

- Use production WSGI server
- Configure reverse proxy
- Set up monitoring
- Implement backup strategies

### CI/CD Pipeline

- Automated testing
- Code quality checks
- Security scanning
- Automated deployment

## Contributing Guidelines

### Code Review Process

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request
6. Code review
7. Merge to main

### Pull Request Checklist

- [ ] Tests pass
- [ ] Code is formatted
- [ ] Documentation updated
- [ ] No security issues
- [ ] Performance considered
- [ ] Error handling implemented

### Release Process

1. Update version number
2. Update changelog
3. Create release tag
4. Deploy to production
5. Monitor deployment
6. Update documentation

## Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Tools

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)

### Best Practices

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/best-practices/)
