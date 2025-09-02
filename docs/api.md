# API Reference

## Overview

The Question App API provides comprehensive endpoints for managing Canvas LMS quiz questions, AI-powered feedback generation, and intelligent chat functionality. The API is organized into modular components for better maintainability and separation of concerns.

## Base URL

```
http://localhost:8080
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

```json
{
  "detail": "Error description"
}
```

## API Modules

### Canvas API

Canvas LMS integration endpoints for course and quiz management.

#### Endpoints

##### GET /api/courses

Retrieve all available courses for the authenticated user.

**Response:**

```json
{
  "success": true,
  "courses": [
    {
      "id": 123,
      "name": "Introduction to Computer Science",
      "course_code": "CS101",
      "enrollment_term_id": 1,
      "term": "Fall 2024"
    }
  ]
}
```

##### GET /api/courses/{course_id}/quizzes

Retrieve all quizzes for a specific course.

**Parameters:**

- `course_id` (string): Canvas course ID

**Response:**

```json
{
  "success": true,
  "quizzes": [
    {
      "id": 456,
      "title": "Midterm Exam",
      "description": "Comprehensive midterm examination",
      "question_count": 25,
      "published": true,
      "due_at": "2024-10-15T23:59:00Z",
      "quiz_type": "assignment"
    }
  ]
}
```

##### GET /api/configuration

Get current course and quiz configuration.

**Response:**

```json
{
  "success": true,
  "course_id": "123",
  "quiz_id": "456",
  "canvas_base_url": "https://your-institution.instructure.com"
}
```

##### POST /api/configuration

Update course and quiz configuration.

**Request Body:**

```json
{
  "course_id": "123",
  "quiz_id": "456"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

##### POST /api/fetch-questions

Fetch questions from Canvas API and save them locally.

**Response:**

```json
{
  "success": true,
  "message": "Fetched and saved 25 questions"
}
```

### Questions API

Question management endpoints for CRUD operations and AI feedback generation.

#### Endpoints

##### DELETE /questions/{question_id}

Delete a question from the dataset.

**Parameters:**

- `question_id` (integer): Question ID to delete

**Response:**

```json
{
  "success": true,
  "message": "Question deleted successfully"
}
```

##### GET /questions/new

Show new question creation page.

**Response:** HTML page for creating new questions

##### POST /questions/new

Create a new question.

**Request Body:**

```json
{
  "question_text": "What is the capital of France?",
  "topic": "geography",
  "tags": "capitals, europe",
  "learning_objective": "Identify European capitals",
  "correct_comments": "Correct! Paris is the capital of France.",
  "incorrect_comments": "Incorrect. Please review European geography.",
  "neutral_comments": "Consider the historical significance of Paris.",
  "answers": [
    {
      "id": 1,
      "text": "London",
      "weight": 0.0
    },
    {
      "id": 2,
      "text": "Paris",
      "weight": 100.0
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Question created successfully",
  "question_id": 789
}
```

##### GET /questions/{question_id}

Show question edit page.

**Parameters:**

- `question_id` (integer): Question ID to edit

**Response:** HTML page for editing the question

##### PUT /questions/{question_id}

Update an existing question.

**Parameters:**

- `question_id` (integer): Question ID to update

**Request Body:** Same as POST /questions/new

**Response:**

```json
{
  "success": true,
  "message": "Question updated successfully"
}
```

##### POST /questions/{question_id}/generate-feedback

Generate AI feedback for a question using Azure OpenAI.

**Parameters:**

- `question_id` (integer): Question ID for feedback generation

**Response:**

```json
{
  "success": true,
  "message": "Feedback generated successfully",
  "feedback": {
    "general_feedback": "This question tests knowledge of European geography...",
    "answer_feedback": {
      "answer 1": "London is the capital of England, not France.",
      "answer 2": "Correct! Paris has been the capital of France since 987 CE."
    },
    "token_usage": {
      "prompt_tokens": 150,
      "completion_tokens": 200,
      "total_tokens": 350
    }
  }
}
```

### Chat API

RAG-based chat functionality with vector store integration.

#### Endpoints

##### GET /chat/

Show chat interface page.

**Response:** HTML page for the chat interface

##### POST /chat/message

Process chat messages with RAG using vector store.

**Request Body:**

```json
{
  "message": "What are the key principles of accessibility?",
  "max_chunks": 3
}
```

**Response:**

```json
{
  "success": true,
  "response": "Based on the available context, the key principles of accessibility include...",
  "context_used": [
    "Context 1: Web accessibility guidelines...",
    "Context 2: WCAG principles..."
  ],
  "token_usage": {
    "prompt_tokens": 300,
    "completion_tokens": 150,
    "total_tokens": 450
  }
}
```

##### GET /chat/system-prompt

Show chat system prompt edit page.

**Response:** HTML page for editing chat system prompt

##### POST /chat/system-prompt

Save chat system prompt.

**Request Body:**

```json
{
  "prompt": "You are a helpful educational assistant..."
}
```

**Response:**

```json
{
  "success": true,
  "message": "Chat system prompt saved successfully"
}
```

##### GET /chat/system-prompt/default

Get default chat system prompt.

**Response:**

```json
{
  "prompt": "You are a helpful educational assistant..."
}
```

##### GET /chat/welcome-message

Get chat welcome message.

**Response:**

```json
{
  "message": "Welcome to the Question App chat assistant!"
}
```

##### POST /chat/welcome-message

Save chat welcome message.

**Request Body:**

```json
{
  "message": "Welcome to the Question App chat assistant!"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Welcome message saved successfully"
}
```

##### GET /chat/welcome-message/default

Get default welcome message.

**Response:**

```json
{
  "message": "Welcome to the Question App chat assistant!"
}
```

### Vector Store API

Vector store operations and semantic search functionality.

#### Endpoints

##### POST /vector-store/create

Create ChromaDB vector store from questions.

**Response:**

```json
{
  "success": true,
  "message": "Vector store created successfully with 25 documents",
  "document_count": 25,
  "embedding_model": "nomic-embed-text"
}
```

##### GET /vector-store/search

Search vector store for relevant content.

**Query Parameters:**

- `query` (string): Search query
- `n_results` (integer, optional): Number of results (default: 3)

**Response:**

```json
{
  "success": true,
  "results": [
    {
      "content": "Web accessibility ensures that people with disabilities...",
      "metadata": {
        "question_id": 123,
        "topic": "accessibility"
      },
      "distance": 0.15
    }
  ]
}
```

##### GET /vector-store/status

Get vector store status.

**Response:**

```json
{
  "success": true,
  "exists": true,
  "document_count": 25,
  "embedding_model": "nomic-embed-text",
  "last_updated": "2024-01-15T10:30:00Z"
}
```

##### DELETE /vector-store/

Delete vector store.

**Response:**

```json
{
  "success": true,
  "message": "Vector store deleted successfully"
}
```

### System Prompt API

System prompt management functionality.

#### Endpoints

##### GET /system-prompt/

Show system prompt edit page.

**Response:** HTML page for editing system prompt

##### GET /system-prompt/api

Get current system prompt as JSON.

**Response:**

```json
{
  "prompt": "You are an educational assistant helping with quiz feedback..."
}
```

##### POST /system-prompt/

Save system prompt.

**Request Body:**

```json
{
  "prompt": "You are an educational assistant helping with quiz feedback..."
}
```

**Response:**

```json
{
  "success": true,
  "message": "System prompt saved successfully"
}
```

##### GET /system-prompt/test

Show test system prompt functionality page.

**Response:** HTML page for testing system prompt

### Objectives API

Learning objectives management functionality.

#### Endpoints

##### GET /objectives/

Show learning objectives management page.

**Response:** HTML page for managing learning objectives

##### POST /objectives/

Save learning objectives.

**Request Body:**

```json
{
  "objectives": [
    {
      "text": "Understand web accessibility principles",
      "blooms_level": "understand",
      "priority": "high"
    },
    {
      "text": "Apply accessibility guidelines in practice",
      "blooms_level": "apply",
      "priority": "medium"
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully saved 2 learning objectives"
}
```

### Debug API

Debugging and testing functionality.

#### Endpoints

##### GET /debug/question/{question_id}

Inspect specific question details.

**Parameters:**

- `question_id` (integer): Question ID to debug

**Response:**

```json
{
  "question_found": true,
  "question_id": 123,
  "question_type": "multiple_choice_question",
  "question_text_length": 150,
  "answers_count": 4,
  "has_correct_comments": true,
  "has_incorrect_comments": true,
  "has_neutral_comments": false,
  "question_keys": ["id", "question_text", "answers", "topic"],
  "total_questions": 25
}
```

##### GET /debug/config

Check application configuration status.

**Response:**

```json
{
  "canvas_configured": true,
  "azure_configured": true,
  "has_system_prompt": true,
  "data_file_exists": true,
  "questions_count": 25,
  "azure_endpoint": "https://your-resource.openai.azure.com",
  "azure_deployment_id": "gpt-4",
  "azure_api_version": "2024-02-15-preview",
  "ollama_host": "http://localhost:11434",
  "ollama_embedding_model": "nomic-embed-text"
}
```

##### GET /debug/ollama-test

Test Ollama connection and model availability.

**Response:**

```json
{
  "ollama_available": true,
  "embedding_model_available": true,
  "test_embedding_generated": true,
  "embedding_dimensions": 768,
  "response_time_ms": 150
}
```

## Data Models

### Question Models

#### Answer

```json
{
  "id": 1,
  "text": "Answer text",
  "html": "<p>Answer text</p>",
  "comments": "Feedback for this answer",
  "comments_html": "<p>Feedback for this answer</p>",
  "weight": 100.0
}
```

#### QuestionUpdate

```json
{
  "question_text": "Question text",
  "topic": "general",
  "tags": "tag1, tag2",
  "learning_objective": "Learning objective",
  "correct_comments": "Correct feedback",
  "incorrect_comments": "Incorrect feedback",
  "neutral_comments": "General feedback",
  "correct_comments_html": "<p>Correct feedback</p>",
  "incorrect_comments_html": "<p>Incorrect feedback</p>",
  "neutral_comments_html": "<p>General feedback</p>",
  "answers": []
}
```

#### LearningObjective

```json
{
  "text": "Learning objective text",
  "blooms_level": "understand",
  "priority": "medium"
}
```

#### ConfigurationUpdate

```json
{
  "course_id": "123",
  "quiz_id": "456"
}
```

## Rate Limiting

The API implements rate limiting for Canvas API calls with exponential backoff for 429 responses.

## Error Codes

- `400`: Bad Request - Invalid input or missing parameters
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limited (Canvas API)
- `500`: Internal Server Error - Server error or configuration issue

## Examples

### Complete Workflow Example

1. **Configure Canvas Integration**:

   ```bash
   curl -X POST http://localhost:8080/api/configuration \
     -H "Content-Type: application/json" \
     -d '{"course_id": "123", "quiz_id": "456"}'
   ```

2. **Fetch Questions**:

   ```bash
   curl -X POST http://localhost:8080/api/fetch-questions
   ```

3. **Create Vector Store**:

   ```bash
   curl -X POST http://localhost:8080/vector-store/create
   ```

4. **Generate AI Feedback**:

   ```bash
   curl -X POST http://localhost:8080/questions/1/generate-feedback
   ```

5. **Chat with RAG**:
   ```bash
   curl -X POST http://localhost:8080/chat/message \
     -H "Content-Type: application/json" \
     -d '{"message": "What are accessibility guidelines?", "max_chunks": 3}'
   ```

## SDK and Client Libraries

The API is RESTful and can be used with any HTTP client. Example clients:

- **Python**: `requests`, `httpx`, `aiohttp`
- **JavaScript**: `fetch`, `axios`
- **cURL**: Command-line HTTP client
- **Postman**: API testing and development

## Versioning

The API follows semantic versioning. Current version: 0.3.0

## Support

For API support and questions:

- Check the troubleshooting guide
- Review error responses for detailed information
- Verify configuration and environment setup
- Test endpoints individually for isolation
