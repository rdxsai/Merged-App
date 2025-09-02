# Testing Guide

## Overview

This guide covers testing strategies, test implementation, and best practices for the Question App project.

## Testing Strategy

### Test Pyramid

The project follows the testing pyramid approach:

```
    /\
   /  \     E2E Tests (Few)
  /____\    Integration Tests (Some)
 /______\   Unit Tests (Many)
```

### Test Types

#### Unit Tests

- Test individual functions and classes
- Fast execution
- High coverage
- Mock external dependencies

#### Integration Tests

- Test API endpoints
- Test external service integrations
- Verify data flow between components

#### End-to-End Tests

- Test complete user workflows
- Verify system behavior
- Test real user scenarios

## Test Structure

### Directory Organization

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_core/          # Core module tests
│   ├── test_models/        # Model tests
│   ├── test_services/      # Service tests
│   └── test_utils/         # Utility tests
├── integration/            # Integration tests
│   ├── __init__.py
│   └── test_api/          # API endpoint tests
├── e2e/                   # End-to-end tests
│   ├── __init__.py
│   └── test_full_app.py   # Full application tests
└── README.md              # Test documentation
```

### Test File Naming

- Unit tests: `test_*.py`
- Integration tests: `test_*.py`
- E2E tests: `test_*.py`
- Fixtures: `conftest.py`

## Test Configuration

### pytest Configuration

**File**: `pytest.ini`

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    api: API tests
    canvas: Canvas integration tests
    ai: AI service tests
```

### Test Dependencies

**File**: `pyproject.toml`

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.0.0"
pytest-mock = "^3.10.0"
httpx = "^0.24.0"
```

## Unit Testing

### Core Module Tests

#### Configuration Tests

**File**: `tests/unit/test_core/test_config.py`

```python
import pytest
from unittest.mock import patch
from src.question_app.core.config import config

class TestConfig:
    """Test configuration management."""

    def test_canvas_config_validation(self):
        """Test Canvas configuration validation."""
        # Test with valid configuration
        with patch.object(config, 'CANVAS_BASE_URL', 'https://test.instructure.com'):
            with patch.object(config, 'CANVAS_API_TOKEN', 'test_token'):
                with patch.object(config, 'COURSE_ID', '123'):
                    with patch.object(config, 'QUIZ_ID', '456'):
                        assert config.validate_canvas_config() is True

    def test_canvas_config_validation_missing(self):
        """Test Canvas configuration validation with missing values."""
        with patch.object(config, 'CANVAS_BASE_URL', None):
            assert config.validate_canvas_config() is False

    def test_azure_openai_config_validation(self):
        """Test Azure OpenAI configuration validation."""
        # Test with valid configuration
        with patch.object(config, 'AZURE_OPENAI_ENDPOINT', 'https://test.openai.azure.com'):
            with patch.object(config, 'AZURE_OPENAI_SUBSCRIPTION_KEY', 'test_key'):
                with patch.object(config, 'AZURE_OPENAI_DEPLOYMENT_ID', 'gpt-4'):
                    with patch.object(config, 'AZURE_OPENAI_API_VERSION', '2024-02-15-preview'):
                        assert config.validate_azure_openai_config() is True
```

#### Logging Tests

**File**: `tests/unit/test_core/test_logging.py`

```python
import pytest
import logging
from src.question_app.core.logging import setup_logging, get_logger

class TestLogging:
    """Test logging configuration."""

    def test_setup_logging(self):
        """Test logging setup."""
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_get_logger(self):
        """Test logger retrieval."""
        logger = get_logger(__name__)
        assert isinstance(logger, logging.Logger)
        assert logger.name == __name__

    def test_logger_levels(self):
        """Test different logging levels."""
        logger = get_logger(__name__)

        # Test that all levels work without errors
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # All should execute without raising exceptions
        assert True
```

### Model Tests

#### Question Model Tests

**File**: `tests/unit/test_models/test_question.py`

```python
import pytest
from pydantic import ValidationError
from src.question_app.models.question import Answer, Question, QuestionUpdate

class TestAnswer:
    """Test Answer model."""

    def test_valid_answer(self):
        """Test valid answer creation."""
        answer = Answer(
            id=1,
            text="Test answer",
            html="<p>Test answer</p>",
            comments="Test feedback",
            weight=100.0
        )

        assert answer.id == 1
        assert answer.text == "Test answer"
        assert answer.html == "<p>Test answer</p>"
        assert answer.comments == "Test feedback"
        assert answer.weight == 100.0

    def test_answer_defaults(self):
        """Test answer with default values."""
        answer = Answer(id=1, text="Test answer")

        assert answer.html == ""
        assert answer.comments == ""
        assert answer.comments_html == ""
        assert answer.weight == 0.0

    def test_invalid_answer(self):
        """Test invalid answer creation."""
        with pytest.raises(ValidationError):
            Answer(id="invalid", text="Test answer")

class TestQuestion:
    """Test Question model."""

    def test_valid_question(self):
        """Test valid question creation."""
        question = Question(
            id=1,
            quiz_id=123,
            question_name="Test Question",
            question_type="multiple_choice_question",
            question_text="What is the capital of France?",
            points_possible=1.0,
            answers=[
                Answer(id=1, text="Paris", weight=100.0),
                Answer(id=2, text="London", weight=0.0)
            ]
        )

        assert question.id == 1
        assert question.quiz_id == 123
        assert question.question_name == "Test Question"
        assert len(question.answers) == 2

    def test_question_with_feedback(self):
        """Test question with feedback comments."""
        question = Question(
            id=1,
            quiz_id=123,
            question_name="Test Question",
            question_type="multiple_choice_question",
            question_text="Test question",
            points_possible=1.0,
            correct_comments="Correct!",
            incorrect_comments="Incorrect.",
            neutral_comments="General feedback"
        )

        assert question.correct_comments == "Correct!"
        assert question.incorrect_comments == "Incorrect."
        assert question.neutral_comments == "General feedback"

class TestQuestionUpdate:
    """Test QuestionUpdate model."""

    def test_valid_question_update(self):
        """Test valid question update."""
        update = QuestionUpdate(
            question_text="Updated question",
            topic="geography",
            tags="capitals, europe",
            learning_objective="Identify European capitals",
            answers=[
                Answer(id=1, text="Paris", weight=100.0),
                Answer(id=2, text="London", weight=0.0)
            ]
        )

        assert update.question_text == "Updated question"
        assert update.topic == "geography"
        assert update.tags == "capitals, europe"
        assert update.learning_objective == "Identify European capitals"
        assert len(update.answers) == 2

    def test_question_update_defaults(self):
        """Test question update with default values."""
        update = QuestionUpdate(question_text="Test question")

        assert update.topic == "general"
        assert update.tags == ""
        assert update.learning_objective == ""
        assert update.answers == []
```

### Service Tests

#### AI Service Tests

**File**: `tests/unit/test_services/test_ai_service.py`

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from src.question_app.services.ai_service import generate_feedback_with_ai

class TestAIService:
    """Test AI service functionality."""

    @pytest.mark.asyncio
    async def test_generate_feedback_success(self):
        """Test successful feedback generation."""
        question_data = {
            "id": 1,
            "question_text": "What is the capital of France?",
            "answers": [
                {"id": 1, "text": "Paris", "weight": 100.0},
                {"id": 2, "text": "London", "weight": 0.0}
            ]
        }

        system_prompt = "You are an educational assistant."

        mock_response = {
            "choices": [{
                "message": {
                    "content": '{"general_feedback": "Test feedback", "answer_feedback": {"answer 1": "Correct!", "answer 2": "Incorrect."}}'
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            result = await generate_feedback_with_ai(question_data, system_prompt)

            assert "general_feedback" in result
            assert "answer_feedback" in result
            assert "token_usage" in result
            assert result["general_feedback"] == "Test feedback"

    @pytest.mark.asyncio
    async def test_generate_feedback_api_error(self):
        """Test feedback generation with API error."""
        question_data = {"id": 1, "question_text": "Test", "answers": []}
        system_prompt = "Test prompt"

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("API Error")

            with pytest.raises(HTTPException) as exc_info:
                await generate_feedback_with_ai(question_data, system_prompt)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_generate_feedback_invalid_response(self):
        """Test feedback generation with invalid response."""
        question_data = {"id": 1, "question_text": "Test", "answers": []}
        system_prompt = "Test prompt"

        mock_response = {
            "choices": [{
                "message": {
                    "content": "Invalid JSON response"
                }
            }]
        }

        with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await generate_feedback_with_ai(question_data, system_prompt)

            assert exc_info.value.status_code == 500
```

### Utility Tests

#### File Utility Tests

**File**: `tests/unit/test_utils/test_file_utils.py`

```python
import pytest
import json
import tempfile
import os
from pathlib import Path
from src.question_app.utils.file_utils import load_json, save_json

class TestFileUtils:
    """Test file utility functions."""

    def test_load_json_existing_file(self):
        """Test loading JSON from existing file."""
        test_data = {"test": "data", "number": 42}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            result = load_json(temp_file)
            assert result == test_data
        finally:
            os.unlink(temp_file)

    def test_load_json_nonexistent_file(self):
        """Test loading JSON from nonexistent file."""
        result = load_json("nonexistent_file.json")
        assert result == []

    def test_load_json_nonexistent_file_with_default(self):
        """Test loading JSON from nonexistent file with custom default."""
        result = load_json("nonexistent_file.json", default={"default": "value"})
        assert result == {"default": "value"}

    def test_save_json_success(self):
        """Test successful JSON saving."""
        test_data = {"test": "data", "list": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_file = f.name

        try:
            result = save_json(temp_file, test_data)
            assert result is True

            # Verify file was created and contains correct data
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            assert saved_data == test_data
        finally:
            os.unlink(temp_file)

    def test_save_json_directory_creation(self):
        """Test JSON saving with directory creation."""
        test_data = {"test": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "subdir", "test.json")

            result = save_json(file_path, test_data)
            assert result is True

            # Verify directory was created
            assert os.path.exists(os.path.dirname(file_path))
            assert os.path.exists(file_path)

    def test_save_json_permission_error(self):
        """Test JSON saving with permission error."""
        test_data = {"test": "data"}

        # Try to save to a directory that doesn't exist and can't be created
        with pytest.raises(Exception):
            save_json("/nonexistent/path/test.json", test_data)
```

## Integration Testing

### API Endpoint Tests

#### Canvas API Tests

**File**: `tests/integration/test_api/test_canvas_api.py`

```python
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.question_app.main import app

client = TestClient(app)

class TestCanvasAPI:
    """Test Canvas API endpoints."""

    def test_get_courses_success(self):
        """Test successful course retrieval."""
        mock_courses = [
            {
                "id": 123,
                "name": "Test Course",
                "course_code": "TEST101",
                "enrollment_term_id": 1,
                "term": "Fall 2024"
            }
        ]

        with patch('src.question_app.api.canvas.fetch_courses', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_courses

            response = client.get("/api/courses")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "courses" in data
            assert len(data["courses"]) == 1
            assert data["courses"][0]["id"] == 123

    def test_get_courses_error(self):
        """Test course retrieval with error."""
        with patch('src.question_app.api.canvas.fetch_courses', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")

            response = client.get("/api/courses")

            assert response.status_code == 500

    def test_get_quizzes_success(self):
        """Test successful quiz retrieval."""
        mock_quizzes = [
            {
                "id": 456,
                "title": "Test Quiz",
                "description": "Test quiz description",
                "question_count": 10,
                "published": True,
                "due_at": "2024-10-15T23:59:00Z",
                "quiz_type": "assignment"
            }
        ]

        with patch('src.question_app.api.canvas.fetch_quizzes', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_quizzes

            response = client.get("/api/courses/123/quizzes")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "quizzes" in data
            assert len(data["quizzes"]) == 1
            assert data["quizzes"][0]["id"] == 456

    def test_get_configuration(self):
        """Test configuration retrieval."""
        with patch('src.question_app.core.config.config') as mock_config:
            mock_config.COURSE_ID = "123"
            mock_config.QUIZ_ID = "456"
            mock_config.CANVAS_BASE_URL = "https://test.instructure.com"

            response = client.get("/api/configuration")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["course_id"] == "123"
            assert data["quiz_id"] == "456"
            assert data["canvas_base_url"] == "https://test.instructure.com"

    def test_update_configuration(self):
        """Test configuration update."""
        config_data = {
            "course_id": "789",
            "quiz_id": "101"
        }

        with patch('src.question_app.core.config.config') as mock_config:
            response = client.post("/api/configuration", json=config_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Configuration updated successfully"

            # Verify configuration was updated
            assert mock_config.COURSE_ID == "789"
            assert mock_config.QUIZ_ID == "101"

    def test_fetch_questions_success(self):
        """Test successful question fetching."""
        mock_questions = [
            {
                "id": 1,
                "question_text": "Test question",
                "question_type": "multiple_choice_question",
                "answers": []
            }
        ]

        with patch('src.question_app.api.canvas.fetch_all_questions', new_callable=AsyncMock) as mock_fetch:
            with patch('src.question_app.api.canvas.save_questions') as mock_save:
                mock_fetch.return_value = mock_questions
                mock_save.return_value = True

                response = client.post("/api/fetch-questions")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "Fetched and saved 1 questions" in data["message"]
```

#### Questions API Tests

**File**: `tests/integration/test_api/test_questions_api.py`

```python
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.question_app.main import app

client = TestClient(app)

class TestQuestionsAPI:
    """Test Questions API endpoints."""

    def test_delete_question_success(self):
        """Test successful question deletion."""
        mock_questions = [
            {"id": 1, "question_text": "Question 1"},
            {"id": 2, "question_text": "Question 2"}
        ]

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            with patch('src.question_app.api.questions.save_questions') as mock_save:
                mock_load.return_value = mock_questions
                mock_save.return_value = True

                response = client.delete("/questions/1")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "Question deleted successfully"

                # Verify save was called with filtered questions
                mock_save.assert_called_once()
                saved_questions = mock_save.call_args[0][0]
                assert len(saved_questions) == 1
                assert saved_questions[0]["id"] == 2

    def test_delete_question_not_found(self):
        """Test question deletion with non-existent question."""
        mock_questions = [{"id": 1, "question_text": "Question 1"}]

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            with patch('src.question_app.api.questions.save_questions') as mock_save:
                mock_load.return_value = mock_questions
                mock_save.return_value = True

                response = client.delete("/questions/999")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

                # Verify save was called with original questions
                mock_save.assert_called_once_with(mock_questions)

    def test_create_question_success(self):
        """Test successful question creation."""
        question_data = {
            "question_text": "New question",
            "topic": "general",
            "tags": "test",
            "learning_objective": "Test objective",
            "answers": [
                {"id": 1, "text": "Answer 1", "weight": 100.0},
                {"id": 2, "text": "Answer 2", "weight": 0.0}
            ]
        }

        mock_questions = [{"id": 1, "question_text": "Existing question"}]

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            with patch('src.question_app.api.questions.save_questions') as mock_save:
                mock_load.return_value = mock_questions
                mock_save.return_value = True

                response = client.post("/questions/new", json=question_data)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "Question created successfully"
                assert data["question_id"] == 2  # Next ID after existing

                # Verify save was called with new question
                mock_save.assert_called_once()
                saved_questions = mock_save.call_args[0][0]
                assert len(saved_questions) == 2
                assert saved_questions[1]["question_text"] == "New question"

    def test_update_question_success(self):
        """Test successful question update."""
        question_data = {
            "question_text": "Updated question",
            "topic": "updated",
            "tags": "updated",
            "learning_objective": "Updated objective",
            "answers": [
                {"id": 1, "text": "Updated answer", "weight": 100.0}
            ]
        }

        mock_questions = [{"id": 1, "question_text": "Original question"}]

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            with patch('src.question_app.api.questions.save_questions') as mock_save:
                mock_load.return_value = mock_questions
                mock_save.return_value = True

                response = client.put("/questions/1", json=question_data)

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "Question updated successfully"

                # Verify save was called with updated question
                mock_save.assert_called_once()
                saved_questions = mock_save.call_args[0][0]
                assert saved_questions[0]["question_text"] == "Updated question"

    def test_update_question_not_found(self):
        """Test question update with non-existent question."""
        question_data = {"question_text": "Updated question"}

        mock_questions = [{"id": 1, "question_text": "Existing question"}]

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            mock_load.return_value = mock_questions

            response = client.put("/questions/999", json=question_data)

            assert response.status_code == 404
            data = response.json()
            assert data["detail"] == "Question not found"

    @pytest.mark.asyncio
    async def test_generate_feedback_success(self):
        """Test successful feedback generation."""
        mock_question = {
            "id": 1,
            "question_text": "Test question",
            "answers": [
                {"id": 1, "text": "Answer 1", "weight": 100.0},
                {"id": 2, "text": "Answer 2", "weight": 0.0}
            ]
        }

        mock_feedback = {
            "general_feedback": "Test general feedback",
            "answer_feedback": {
                "answer 1": "Correct!",
                "answer 2": "Incorrect."
            },
            "token_usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            with patch('src.question_app.api.questions.load_system_prompt') as mock_prompt:
                with patch('src.question_app.api.questions.generate_feedback_with_ai', new_callable=AsyncMock) as mock_ai:
                    with patch('src.question_app.api.questions.save_questions') as mock_save:
                        mock_load.return_value = [mock_question]
                        mock_prompt.return_value = "Test system prompt"
                        mock_ai.return_value = mock_feedback
                        mock_save.return_value = True

                        response = client.post("/questions/1/generate-feedback")

                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True
                        assert data["message"] == "Feedback generated successfully"
                        assert "feedback" in data
```

## End-to-End Testing

### Full Application Tests

**File**: `tests/e2e/test_full_app.py`

```python
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.question_app.main import app

client = TestClient(app)

class TestFullApp:
    """Test complete application workflows."""

    def test_home_page_loads(self):
        """Test that home page loads successfully."""
        with patch('src.question_app.main.load_questions') as mock_load:
            mock_load.return_value = []

            response = client.get("/")

            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_complete_question_workflow(self):
        """Test complete question management workflow."""
        # 1. Create a question
        question_data = {
            "question_text": "E2E test question",
            "topic": "testing",
            "tags": "e2e, test",
            "learning_objective": "Test E2E workflow",
            "answers": [
                {"id": 1, "text": "Correct answer", "weight": 100.0},
                {"id": 2, "text": "Wrong answer", "weight": 0.0}
            ]
        }

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            with patch('src.question_app.api.questions.save_questions') as mock_save:
                mock_load.return_value = []
                mock_save.return_value = True

                # Create question
                create_response = client.post("/questions/new", json=question_data)
                assert create_response.status_code == 200
                question_id = create_response.json()["question_id"]

                # Update mock to include new question
                mock_load.return_value = [{"id": question_id, **question_data}]

                # Update question
                update_data = {**question_data, "question_text": "Updated E2E test question"}
                update_response = client.put(f"/questions/{question_id}", json=update_data)
                assert update_response.status_code == 200

                # Delete question
                delete_response = client.delete(f"/questions/{question_id}")
                assert delete_response.status_code == 200

    def test_canvas_integration_workflow(self):
        """Test complete Canvas integration workflow."""
        mock_courses = [{"id": 123, "name": "Test Course"}]
        mock_quizzes = [{"id": 456, "title": "Test Quiz"}]
        mock_questions = [{"id": 1, "question_text": "Test question"}]

        # Test course retrieval
        with patch('src.question_app.api.canvas.fetch_courses', new_callable=AsyncMock) as mock_fetch_courses:
            mock_fetch_courses.return_value = mock_courses

            response = client.get("/api/courses")
            assert response.status_code == 200
            assert len(response.json()["courses"]) == 1

        # Test quiz retrieval
        with patch('src.question_app.api.canvas.fetch_quizzes', new_callable=AsyncMock) as mock_fetch_quizzes:
            mock_fetch_quizzes.return_value = mock_quizzes

            response = client.get("/api/courses/123/quizzes")
            assert response.status_code == 200
            assert len(response.json()["quizzes"]) == 1

        # Test question fetching
        with patch('src.question_app.api.canvas.fetch_all_questions', new_callable=AsyncMock) as mock_fetch_questions:
            with patch('src.question_app.api.canvas.save_questions') as mock_save:
                mock_fetch_questions.return_value = mock_questions
                mock_save.return_value = True

                response = client.post("/api/fetch-questions")
                assert response.status_code == 200
                assert "Fetched and saved 1 questions" in response.json()["message"]

    def test_ai_feedback_workflow(self):
        """Test AI feedback generation workflow."""
        mock_question = {
            "id": 1,
            "question_text": "AI test question",
            "answers": [{"id": 1, "text": "Answer", "weight": 100.0}]
        }

        mock_feedback = {
            "general_feedback": "AI generated feedback",
            "answer_feedback": {"answer 1": "Correct answer feedback"},
            "token_usage": {"total_tokens": 100}
        }

        with patch('src.question_app.api.questions.load_questions') as mock_load:
            with patch('src.question_app.api.questions.load_system_prompt') as mock_prompt:
                with patch('src.question_app.api.questions.generate_feedback_with_ai', new_callable=AsyncMock) as mock_ai:
                    with patch('src.question_app.api.questions.save_questions') as mock_save:
                        mock_load.return_value = [mock_question]
                        mock_prompt.return_value = "Test system prompt"
                        mock_ai.return_value = mock_feedback
                        mock_save.return_value = True

                        response = client.post("/questions/1/generate-feedback")
                        assert response.status_code == 200
                        assert response.json()["success"] is True
```

## Test Fixtures

### Shared Fixtures

**File**: `tests/conftest.py`

```python
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from src.question_app.main import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)

@pytest.fixture
def sample_question():
    """Sample question data fixture."""
    return {
        "id": 1,
        "question_text": "What is the capital of France?",
        "question_type": "multiple_choice_question",
        "points_possible": 1.0,
        "topic": "geography",
        "tags": "capitals, europe",
        "learning_objective": "Identify European capitals",
        "answers": [
            {"id": 1, "text": "Paris", "weight": 100.0},
            {"id": 2, "text": "London", "weight": 0.0},
            {"id": 3, "text": "Berlin", "weight": 0.0},
            {"id": 4, "text": "Madrid", "weight": 0.0}
        ]
    }

@pytest.fixture
def sample_questions(sample_question):
    """Sample questions list fixture."""
    return [sample_question]

@pytest.fixture
def sample_system_prompt():
    """Sample system prompt fixture."""
    return "You are an educational assistant helping with quiz feedback generation."

@pytest.fixture
def sample_ai_response():
    """Sample AI response fixture."""
    return {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "general_feedback": "This question tests knowledge of European geography.",
                    "answer_feedback": {
                        "answer 1": "Correct! Paris is the capital of France.",
                        "answer 2": "Incorrect. London is the capital of England.",
                        "answer 3": "Incorrect. Berlin is the capital of Germany.",
                        "answer 4": "Incorrect. Madrid is the capital of Spain."
                    }
                })
            }
        }],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 200,
            "total_tokens": 350
        }
    }

@pytest.fixture
def temp_data_file():
    """Temporary data file fixture."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([], f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    Path(temp_file).unlink(missing_ok=True)

@pytest.fixture
def mock_canvas_config():
    """Mock Canvas configuration fixture."""
    with patch('src.question_app.core.config.config') as mock_config:
        mock_config.CANVAS_BASE_URL = "https://test.instructure.com"
        mock_config.CANVAS_API_TOKEN = "test_token"
        mock_config.COURSE_ID = "123"
        mock_config.QUIZ_ID = "456"
        yield mock_config

@pytest.fixture
def mock_azure_config():
    """Mock Azure OpenAI configuration fixture."""
    with patch('src.question_app.core.config.config') as mock_config:
        mock_config.AZURE_OPENAI_ENDPOINT = "https://test.openai.azure.com"
        mock_config.AZURE_OPENAI_SUBSCRIPTION_KEY = "test_key"
        mock_config.AZURE_OPENAI_DEPLOYMENT_ID = "gpt-4"
        mock_config.AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
        yield mock_config
```

## Test Execution

### Running Tests

#### All Tests

```bash
# Run all tests
poetry run test

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run test --coverage
```

#### Specific Test Types

```bash
# Run only unit tests
poetry run pytest -m unit

# Run only integration tests
poetry run pytest -m integration

# Run only E2E tests
poetry run pytest -m e2e

# Run only API tests
poetry run pytest -m api
```

#### Specific Test Files

```bash
# Run specific test file
poetry run pytest tests/unit/test_core/test_config.py

# Run specific test class
poetry run pytest tests/unit/test_core/test_config.py::TestConfig

# Run specific test method
poetry run pytest tests/unit/test_core/test_config.py::TestConfig::test_canvas_config_validation
```

### Test Coverage

#### Coverage Configuration

**File**: `pyproject.toml`

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]
```

#### Coverage Commands

```bash
# Generate coverage report
poetry run test --coverage

# For detailed coverage options, see the unified test runner documentation
```

### Continuous Integration

#### GitHub Actions

**File**: `.github/workflows/test.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -

      - name: Install dependencies
        run: poetry install

      - name: Run tests
        run: poetry run test --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Best Practices

### Test Organization

- Group related tests in classes
- Use descriptive test method names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent and isolated

### Mocking Strategy

- Mock external dependencies
- Use realistic mock data
- Test error conditions
- Verify mock interactions

### Test Data Management

- Use fixtures for common data
- Create realistic test scenarios
- Clean up test data
- Use factories for complex objects

### Performance Testing

- Monitor test execution time
- Use appropriate test markers
- Parallelize tests when possible
- Optimize slow tests

### Documentation

- Document test purpose and scope
- Include test data examples
- Explain complex test scenarios
- Keep test documentation updated

## Troubleshooting

### Common Issues

#### Import Errors

- Check Python path configuration
- Verify package installation
- Use absolute imports in tests

#### Mock Issues

- Ensure mocks are applied correctly
- Check mock return values
- Verify mock call arguments

#### Async Test Issues

- Use `@pytest.mark.asyncio` for async tests
- Mock async functions properly
- Handle async context managers

#### Coverage Issues

- Check coverage configuration
- Verify source paths
- Review exclusion patterns

### Debugging Tests

#### Verbose Output

```bash
# Run with verbose output
poetry run pytest -v -s

# Run with maximum verbosity
poetry run pytest -vvv -s
```

#### Debug Mode

```bash
# Run with debugger
poetry run pytest --pdb

# Run with debugger on failures
poetry run pytest --pdb-fail
```

#### Test Isolation

```bash
# Run single test
poetry run pytest tests/unit/test_core/test_config.py::TestConfig::test_canvas_config_validation -v -s
```

## Resources

### Testing Tools

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)

### Best Practices

- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Best Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)

### Examples

- [FastAPI Testing Examples](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Examples](https://docs.pytest.org/en/stable/example/index.html)
- [Mock Examples](https://docs.python.org/3/library/unittest.mock-examples.html)
