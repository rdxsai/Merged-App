# API Structure Documentation

## Overview

The Question App API has been restructured to organize endpoints by functionality. Canvas-related endpoints have been extracted into a dedicated module for better maintainability and separation of concerns.

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

## Integration

The Canvas API router is automatically included in the main FastAPI application:

```python
from .api import canvas_router
app.include_router(canvas_router)
```

## Benefits

1. **Modularity**: Canvas functionality is isolated in its own module
2. **Maintainability**: Easier to maintain and update Canvas-specific code
3. **Testability**: Canvas endpoints can be tested independently
4. **Scalability**: Easy to add more API modules for other functionality
5. **Documentation**: Better organization makes the API easier to understand

## Future Extensions

Additional API modules can be created for:

- Question management endpoints
- AI/feedback generation endpoints
- Chat assistant endpoints
- Learning objectives endpoints
- System configuration endpoints

## Usage

The API endpoints maintain the same interface as before, so existing frontend code and integrations will continue to work without changes.
