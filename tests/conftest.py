"""
Pytest configuration and fixtures for question app tests
"""
import json
import os
import tempfile
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from question_app.main import app


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "e2e: mark test as an end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow")


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_questions() -> List[Dict[str, Any]]:
    """Sample questions for testing"""
    return [
        {
            "id": 1,
            "quiz_id": 123,
            "question_name": "Sample Question 1",
            "question_type": "multiple_choice_question",
            "question_text": "What is the capital of France?",
            "points_possible": 1.0,
            "correct_comments": "Great job!",
            "incorrect_comments": "Try again!",
            "neutral_comments": "Paris is the capital of France.",
            "correct_comments_html": "<p>Great job!</p>",
            "incorrect_comments_html": "<p>Try again!</p>",
            "neutral_comments_html": "<p>Paris is the capital of France.</p>",
            "topic": "general",
            "tags": "geography,capitals",
            "learning_objective": "Understand world geography",
            "answers": [
                {
                    "id": 1,
                    "text": "London",
                    "html": "<p>London</p>",
                    "comments": "London is the capital of England, not France.",
                    "comments_html": "<p>London is the capital of England, not France.</p>",
                    "weight": 0.0,
                },
                {
                    "id": 2,
                    "text": "Paris",
                    "html": "<p>Paris</p>",
                    "comments": "Correct! Paris is the capital of France.",
                    "comments_html": "<p>Correct! Paris is the capital of France.</p>",
                    "weight": 100.0,
                },
            ],
        },
        {
            "id": 2,
            "quiz_id": 123,
            "question_name": "Sample Question 2",
            "question_type": "multiple_choice_question",
            "question_text": "Which HTML tag is used for accessibility?",
            "points_possible": 2.0,
            "correct_comments": "Excellent!",
            "incorrect_comments": "Review HTML accessibility.",
            "neutral_comments": "The alt attribute is essential for accessibility.",
            "correct_comments_html": "<p>Excellent!</p>",
            "incorrect_comments_html": "<p>Review HTML accessibility.</p>",
            "neutral_comments_html": "<p>The alt attribute is essential for accessibility.</p>",
            "topic": "accessibility",
            "tags": "html,accessibility,web",
            "learning_objective": "Understand HTML accessibility features",
            "answers": [
                {
                    "id": 1,
                    "text": "&lt;img&gt;",
                    "html": "<p>&lt;img&gt;</p>",
                    "comments": "The img tag itself is not for accessibility.",
                    "comments_html": "<p>The img tag itself is not for accessibility.</p>",
                    "weight": 0.0,
                },
                {
                    "id": 2,
                    "text": "&lt;aria-label&gt;",
                    "html": "<p>&lt;aria-label&gt;</p>",
                    "comments": "Correct! ARIA labels provide accessibility information.",
                    "comments_html": "<p>Correct! ARIA labels provide accessibility information.</p>",
                    "weight": 100.0,
                },
            ],
        },
    ]


@pytest.fixture
def sample_objectives() -> List[Dict[str, Any]]:
    """Sample learning objectives for testing"""
    return [
        {
            "text": "Understand basic accessibility principles",
            "blooms_level": "understand",
            "priority": "high",
        },
        {
            "text": "Apply accessibility guidelines in web development",
            "blooms_level": "apply",
            "priority": "medium",
        },
    ]


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        "CANVAS_API_TOKEN": "test_token",
        "CANVAS_BASE_URL": "https://test.instructure.com",
        "AZURE_OPENAI_SUBSCRIPTION_KEY": "test_key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT_ID": "test_deployment",
        "COURSE_ID": "123",
        "QUIZ_ID": "456",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        questions_file = os.path.join(temp_dir, "quiz_questions.json")
        with open(questions_file, "w") as f:
            json.dump([], f)

        objectives_file = os.path.join(temp_dir, "learning_objectives.json")
        with open(objectives_file, "w") as f:
            json.dump([], f)

        system_prompt_file = os.path.join(temp_dir, "system_prompt.txt")
        with open(system_prompt_file, "w") as f:
            f.write("You are a helpful assistant for quiz questions.")

        yield temp_dir


@pytest.fixture
def mock_ai_service():
    """Mock AI service responses"""
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "Answer 1: London is the capital of England, not France. Answer 2: Correct! Paris is the capital of France."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
        },
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.json.return_value = mock_response
        mock_post.return_value = mock_http_response
        yield mock_response
