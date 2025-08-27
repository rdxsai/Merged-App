"""
Pytest configuration and fixtures for question app tests
"""
import asyncio
import json
import os
import sys
import tempfile
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Import the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
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
                {
                    "id": 3,
                    "text": "Berlin",
                    "html": "<p>Berlin</p>",
                    "comments": "Berlin is the capital of Germany, not France.",
                    "comments_html": "<p>Berlin is the capital of Germany, not France.</p>",
                    "weight": 0.0,
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
            "tags": "html,accessibility,alt",
            "learning_objective": "Understand HTML accessibility features",
            "answers": [
                {
                    "id": 1,
                    "text": "alt",
                    "html": "<p>alt</p>",
                    "comments": "Correct! The alt attribute provides alternative text for images.",
                    "comments_html": "<p>Correct! The alt attribute provides alternative text for images.</p>",
                    "weight": 100.0,
                },
                {
                    "id": 2,
                    "text": "title",
                    "html": "<p>title</p>",
                    "comments": "The title attribute provides tooltips, not accessibility for screen readers.",
                    "comments_html": "<p>The title attribute provides tooltips, not accessibility for screen readers.</p>",
                    "weight": 0.0,
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
            "text": "Apply WCAG guidelines in web development",
            "blooms_level": "apply",
            "priority": "medium",
        },
    ]


@pytest.fixture
def temp_data_file():
    """Create a temporary data file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([], f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_system_prompt_file():
    """Create a temporary system prompt file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("You are a helpful assistant for quiz questions.")
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        "CANVAS_BASE_URL": "https://canvas.test.com",
        "CANVAS_API_TOKEN": "test_token",
        "COURSE_ID": "123",
        "QUIZ_ID": "456",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT_ID": "test-deployment",
        "AZURE_OPENAI_API_VERSION": "2023-12-01-preview",
        "AZURE_OPENAI_SUBSCRIPTION_KEY": "test_key",
        "OLLAMA_HOST": "http://localhost:11434",
        "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing HTTP requests"""
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_client.return_value
        mock_client.return_value.__aexit__.return_value = None
        yield mock_client.return_value


@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB for testing vector store operations"""
    with patch("chromadb.PersistentClient") as mock_client:
        mock_collection = MagicMock()
        mock_client.return_value.get_collection.return_value = mock_collection
        mock_client.return_value.create_collection.return_value = mock_collection
        yield mock_client.return_value


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Configure pytest
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
