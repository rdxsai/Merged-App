# API Structure Documentation

## Overview

The Question App API has been restructured to organize endpoints by functionality. Both Canvas-related and question-related endpoints have been extracted into dedicated modules for better maintainability and separation of concerns.

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
- AI feedback generation integration
- Proper error handling and logging
- Backward compatibility with existing data structure

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
from .api import canvas_router, questions_router
app.include_router(canvas_router)
app.include_router(questions_router)
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

- Learning objectives management
- System configuration
- Chat assistant functionality
- Vector store management
- User authentication and authorization

## Usage

The API endpoints maintain the same interface as before, so existing frontend code and integrations will continue to work without changes.
