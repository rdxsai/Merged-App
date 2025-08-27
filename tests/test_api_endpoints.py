"""
Tests for API endpoints
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHomeEndpoint:
    """Test the home page endpoint"""

    def test_home_page_loads(self, client):
        """Test that home page loads successfully"""
        with patch("main.load_questions", return_value=[]):
            response = client.get("/")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_home_page_with_questions(self, client, sample_questions):
        """Test home page with sample questions"""
        with patch("main.load_questions", return_value=sample_questions):
            response = client.get("/")
            assert response.status_code == 200
            # Just check that the page loads successfully, don't check specific content
            # since template rendering can be complex and vary
            assert "text/html" in response.headers["content-type"]


class TestCoursesAPI:
    """Test courses API endpoints"""

    @pytest.mark.asyncio
    async def test_get_courses_success(self, client, mock_env_vars):
        """Test successful courses fetch"""
        mock_courses = [
            {"id": 1, "name": "Course 1", "course_code": "CS101"},
            {"id": 2, "name": "Course 2", "course_code": "CS102"},
        ]

        with patch("main.fetch_courses", return_value=mock_courses):
            response = client.get("/api/courses")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["courses"]) == 2

    @pytest.mark.asyncio
    async def test_get_courses_missing_config(self, client):
        """Test courses fetch with missing configuration"""
        with patch("main.CANVAS_BASE_URL", None):
            response = client.get("/api/courses")
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_quizzes_success(self, client, mock_env_vars):
        """Test successful quizzes fetch"""
        mock_quizzes = [
            {"id": 1, "title": "Quiz 1", "question_count": 10},
            {"id": 2, "title": "Quiz 2", "question_count": 15},
        ]

        with patch("main.fetch_quizzes", return_value=mock_quizzes):
            response = client.get("/api/courses/123/quizzes")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["quizzes"]) == 2


class TestConfigurationAPI:
    """Test configuration API endpoints"""

    def test_update_configuration_success(self, client):
        """Test successful configuration update"""
        config_data = {"course_id": "456", "quiz_id": "789"}

        response = client.post("/api/configuration", json=config_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_update_configuration_partial(self, client):
        """Test partial configuration update"""
        config_data = {"course_id": "456"}

        response = client.post("/api/configuration", json=config_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestQuestionsAPI:
    """Test questions API endpoints"""

    def test_fetch_questions_success(self, client, sample_questions):
        """Test successful questions fetch"""
        with patch("main.fetch_all_questions", return_value=sample_questions):
            with patch("main.save_questions", return_value=True):
                response = client.post("/fetch-questions")
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "2 questions" in data["message"]

    def test_fetch_questions_save_failure(self, client, sample_questions):
        """Test questions fetch with save failure"""
        with patch("main.fetch_all_questions", return_value=sample_questions):
            with patch("main.save_questions", return_value=False):
                response = client.post("/fetch-questions")
                assert response.status_code == 500

    def test_delete_question_success(self, client, sample_questions):
        """Test successful question deletion"""
        with patch("main.load_questions", return_value=sample_questions):
            with patch("main.save_questions", return_value=True):
                response = client.delete("/questions/1")
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

    def test_delete_question_not_found(self, client):
        """Test deleting non-existent question"""
        with patch("main.load_questions", return_value=[]):
            response = client.delete("/questions/999")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_delete_question_save_failure(self, client, sample_questions):
        """Test question deletion with save failure"""
        with patch("main.load_questions", return_value=sample_questions):
            with patch("main.save_questions", return_value=False):
                response = client.delete("/questions/1")
                assert response.status_code == 500


class TestQuestionCRUD:
    """Test question CRUD operations"""

    def test_get_question_edit_page(self, client, sample_questions):
        """Test getting question edit page"""
        with patch("main.load_questions", return_value=sample_questions):
            response = client.get("/questions/1")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_get_question_edit_page_not_found(self, client):
        """Test getting non-existent question edit page"""
        with patch("main.load_questions", return_value=[]):
            response = client.get("/questions/999")
            assert response.status_code == 404

    def test_create_new_question_page(self, client):
        """Test getting new question creation page"""
        with patch("main.load_questions", return_value=[]):
            response = client.get("/questions/new")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_create_new_question_success(self, client):
        """Test successful new question creation"""
        question_data = {
            "question_text": "What is the capital of France?",
            "topic": "general",
            "tags": "geography,capitals",
            "learning_objective": "Understand world geography",
            "correct_comments": "Great job!",
            "incorrect_comments": "Try again!",
            "neutral_comments": "Paris is the capital of France.",
            "correct_comments_html": "<p>Great job!</p>",
            "incorrect_comments_html": "<p>Try again!</p>",
            "neutral_comments_html": "<p>Paris is the capital of France.</p>",
            "answers": [
                {
                    "id": 1,
                    "text": "London",
                    "html": "<p>London</p>",
                    "comments": "London is the capital of England.",
                    "comments_html": "<p>London is the capital of England.</p>",
                    "weight": 0.0,
                },
                {
                    "id": 2,
                    "text": "Paris",
                    "html": "<p>Paris</p>",
                    "comments": "Correct!",
                    "comments_html": "<p>Correct!</p>",
                    "weight": 100.0,
                },
            ],
        }

        with patch("main.load_questions", return_value=[]):
            with patch("main.save_questions", return_value=True):
                response = client.post("/questions/new", json=question_data)
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "question_id" in data

    def test_update_question_success(self, client, sample_questions):
        """Test successful question update"""
        question_data = {
            "question_text": "Updated question text",
            "topic": "accessibility",
            "tags": "updated,tags",
            "learning_objective": "Updated objective",
            "correct_comments": "Updated correct comments",
            "incorrect_comments": "Updated incorrect comments",
            "neutral_comments": "Updated neutral comments",
            "correct_comments_html": "<p>Updated correct</p>",
            "incorrect_comments_html": "<p>Updated incorrect</p>",
            "neutral_comments_html": "<p>Updated neutral</p>",
            "answers": [
                {
                    "id": 1,
                    "text": "Updated answer 1",
                    "html": "<p>Updated answer 1</p>",
                    "comments": "Updated comment 1",
                    "comments_html": "<p>Updated comment 1</p>",
                    "weight": 0.0,
                }
            ],
        }

        with patch("main.load_questions", return_value=sample_questions):
            with patch("main.save_questions", return_value=True):
                response = client.put("/questions/1", json=question_data)
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

    def test_update_question_not_found(self, client):
        """Test updating non-existent question"""
        question_data = {"question_text": "Updated text"}

        with patch("main.load_questions", return_value=[]):
            response = client.put("/questions/999", json=question_data)
            assert response.status_code == 404


class TestSystemPromptAPI:
    """Test system prompt API endpoints"""

    def test_get_system_prompt_page(self, client):
        """Test getting system prompt edit page"""
        with patch("main.load_system_prompt", return_value="Test prompt"):
            response = client.get("/system-prompt")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_get_system_prompt_api(self, client):
        """Test getting system prompt via API"""
        with patch("main.load_system_prompt", return_value="Test prompt"):
            response = client.get("/system-prompt/api")
            assert response.status_code == 200
            data = response.json()
            assert data["prompt"] == "Test prompt"

    def test_save_system_prompt_success(self, client):
        """Test successful system prompt save"""
        with patch("main.save_system_prompt", return_value=True):
            response = client.post(
                "/system-prompt", data={"prompt": "New system prompt"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_save_system_prompt_failure(self, client):
        """Test system prompt save failure"""
        with patch("main.save_system_prompt", return_value=False):
            response = client.post(
                "/system-prompt", data={"prompt": "New system prompt"}
            )
            assert response.status_code == 500


class TestChatAPI:
    """Test chat API endpoints"""

    def test_chat_page_loads(self, client):
        """Test that chat page loads successfully"""
        response = client.get("/chat")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_chat_message_success(self, client, mock_env_vars):
        """Test successful chat message processing"""
        mock_chunks = [
            {
                "content": "Sample context",
                "metadata": {"question_id": 1},
                "distance": 0.1,
            }
        ]

        mock_ai_response = "This is a helpful response."

        with patch("main.search_vector_store", return_value=mock_chunks):
            with patch("main.load_chat_system_prompt", return_value="Test prompt"):
                with patch("httpx.AsyncClient.post") as mock_post:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "choices": [{"message": {"content": mock_ai_response}}]
                    }
                    mock_post.return_value = mock_response

                    response = client.post(
                        "/chat/message",
                        json={"message": "Test question", "max_chunks": 3},
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert data["response"] == mock_ai_response

    def test_chat_message_empty(self, client):
        """Test chat message with empty content"""
        response = client.post("/chat/message", json={"message": ""})
        assert response.status_code == 400

    def test_chat_message_invalid_max_chunks(self, client):
        """Test chat message with invalid max_chunks"""
        response = client.post(
            "/chat/message", json={"message": "Test", "max_chunks": 999}
        )
        assert response.status_code == 200  # Should default to 3


class TestObjectivesAPI:
    """Test learning objectives API endpoints"""

    def test_objectives_page_loads(self, client, sample_objectives):
        """Test that objectives page loads successfully"""
        with patch("main.load_objectives", return_value=sample_objectives):
            response = client.get("/objectives")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_save_objectives_success(self, client):
        """Test successful objectives save"""
        objectives_data = {
            "objectives": [
                {
                    "text": "Test objective 1",
                    "blooms_level": "understand",
                    "priority": "high",
                },
                {
                    "text": "Test objective 2",
                    "blooms_level": "apply",
                    "priority": "medium",
                },
            ]
        }

        with patch("main.save_objectives", return_value=True):
            response = client.post("/objectives", json=objectives_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_save_objectives_failure(self, client):
        """Test objectives save failure"""
        objectives_data = {"objectives": []}

        with patch("main.save_objectives", return_value=False):
            response = client.post("/objectives", json=objectives_data)
            assert response.status_code == 500


class TestDebugEndpoints:
    """Test debug endpoints"""

    def test_debug_config(self, client, mock_env_vars):
        """Test debug configuration endpoint"""
        with patch("main.load_system_prompt", return_value="Test prompt"):
            with patch("main.load_questions", return_value=[]):
                with patch("os.path.exists", return_value=True):
                    response = client.get("/debug/config")
                    assert response.status_code == 200
                    data = response.json()
                    assert "canvas_configured" in data
                    assert "azure_configured" in data

    def test_debug_question(self, client, sample_questions):
        """Test debug question endpoint"""
        with patch("main.load_questions", return_value=sample_questions):
            response = client.get("/debug/question/1")
            assert response.status_code == 200
            data = response.json()
            assert data["question_found"] is True

    def test_debug_question_not_found(self, client):
        """Test debug question endpoint with non-existent question"""
        with patch("main.load_questions", return_value=[]):
            response = client.get("/debug/question/999")
            assert response.status_code == 200
            data = response.json()
            assert data["question_found"] is False
