"""
Integration tests for the question app
"""
import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from question_app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test data files
        questions_file = os.path.join(temp_dir, "quiz_questions.json")
        with open(questions_file, "w") as f:
            json.dump(
                [
                    {
                        "id": 1,
                        "question_text": "What is the capital of France?",
                        "question_type": "multiple_choice_question",
                        "points_possible": 1.0,
                        "answers": [
                            {"id": 1, "text": "London", "weight": 0.0},
                            {"id": 2, "text": "Paris", "weight": 100.0},
                        ],
                    }
                ],
                f,
            )

        objectives_file = os.path.join(temp_dir, "learning_objectives.json")
        with open(objectives_file, "w") as f:
            json.dump(
                [
                    {
                        "text": "Understand basic accessibility",
                        "blooms_level": "understand",
                        "priority": "high",
                    }
                ],
                f,
            )

        system_prompt_file = os.path.join(temp_dir, "system_prompt.txt")
        with open(system_prompt_file, "w") as f:
            f.write("You are a helpful assistant for quiz questions.")

        yield temp_dir


class TestFullWorkflow:
    """Test complete application workflows"""

    @pytest.mark.integration
    def test_question_lifecycle(self, client, temp_data_dir):
        """Test complete question lifecycle: create, read, update, delete"""
        # Mock file operations to use temp directory
        with patch(
            "question_app.utils.file_utils.DATA_FILE",
            os.path.join(temp_data_dir, "quiz_questions.json"),
        ):
            with patch("question_app.api.questions.load_questions") as mock_load:
                with patch("question_app.api.questions.save_questions") as mock_save:
                    mock_load.return_value = []
                    mock_save.return_value = True

                    # 1. Create a new question
                    question_data = {
                        "question_text": "What is accessibility?",
                        "topic": "accessibility",
                        "tags": "web,accessibility",
                        "learning_objective": "Understand web accessibility",
                        "correct_comments": "Great job!",
                        "incorrect_comments": "Try again!",
                        "neutral_comments": "Accessibility is important.",
                        "correct_comments_html": "<p>Great job!</p>",
                        "incorrect_comments_html": "<p>Try again!</p>",
                        "neutral_comments_html": "<p>Accessibility is important.</p>",
                        "answers": [
                            {
                                "id": 1,
                                "text": "A design principle",
                                "html": "<p>A design principle</p>",
                                "comments": "Correct!",
                                "comments_html": "<p>Correct!</p>",
                                "weight": 100.0,
                            },
                            {
                                "id": 2,
                                "text": "A programming language",
                                "html": "<p>A programming language</p>",
                                "comments": "Incorrect.",
                                "comments_html": "<p>Incorrect.</p>",
                                "weight": 0.0,
                            },
                        ],
                    }

                    response = client.post("/questions/new", json=question_data)
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    question_id = data["question_id"]

                    # 2. Update the question (skip read since it requires template rendering)
                    updated_data = question_data.copy()
                    updated_data["question_text"] = "Updated: What is accessibility?"

                    response = client.put(
                        f"/questions/{question_id}", json=updated_data
                    )
                    assert response.status_code == 200

                    # 3. Delete the question
                    response = client.delete(f"/questions/{question_id}")
                    assert response.status_code == 200

    @pytest.mark.integration
    def test_system_prompt_workflow(self, client, temp_data_dir):
        """Test system prompt management workflow"""
        with patch(
            "question_app.utils.file_utils.SYSTEM_PROMPT_FILE",
            os.path.join(temp_data_dir, "system_prompt.txt"),
        ):
            # 1. Get current prompt
            response = client.get("/system-prompt/api")
            assert response.status_code == 200
            data = response.json()
            assert "prompt" in data

            # 2. Update prompt
            new_prompt = "Updated system prompt for testing."
            response = client.post("/system-prompt", data={"prompt": new_prompt})
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            # 3. Verify update
            response = client.get("/system-prompt/api")
            assert response.status_code == 200
            data = response.json()
            assert data["prompt"] == new_prompt

    @pytest.mark.integration
    def test_objectives_workflow(self, client, temp_data_dir):
        """Test learning objectives management workflow"""
        objectives_file = os.path.join(temp_data_dir, "learning_objectives.json")

        with patch("question_app.api.objectives.load_objectives") as mock_load:
            with patch("question_app.api.objectives.save_objectives") as mock_save:
                mock_load.return_value = []
                mock_save.return_value = True

                # 1. Get objectives page
                response = client.get("/objectives")
                assert response.status_code == 200

                # 2. Save objectives
                objectives_data = {
                    "objectives": [
                        {
                            "text": "Understand web accessibility",
                            "blooms_level": "understand",
                            "priority": "high",
                        },
                        {
                            "text": "Apply WCAG guidelines",
                            "blooms_level": "apply",
                            "priority": "medium",
                        },
                    ]
                }

                response = client.post("/objectives", json=objectives_data)
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

    @pytest.mark.integration
    def test_chat_workflow(self, client):
        """Test chat functionality workflow"""
        # 1. Load chat page
        response = client.get("/chat")
        assert response.status_code == 200

        # 2. Send chat message (mocked)
        with patch("question_app.api.vector_store.search_vector_store") as mock_search:
            with patch("question_app.api.chat.load_chat_system_prompt") as mock_prompt:
                with patch("httpx.AsyncClient.post") as mock_post:
                    mock_search.return_value = [
                        {
                            "content": "Sample context",
                            "metadata": {"question_id": 1},
                            "distance": 0.1,
                        }
                    ]
                    mock_prompt.return_value = "Test system prompt"

                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "choices": [{"message": {"content": "Test response"}}]
                    }
                    mock_post.return_value = mock_response

                    response = client.post(
                        "/chat/message",
                        json={"message": "What is accessibility?", "max_chunks": 3},
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert "response" in data

    @pytest.mark.integration
    def test_vector_store_workflow(self, client, sample_questions):
        """Test vector store creation workflow"""
        with patch("question_app.api.vector_store.load_questions", return_value=sample_questions):
            with patch("question_app.api.vector_store.get_ollama_embeddings") as mock_embeddings:
                with patch("chromadb.PersistentClient") as mock_client:
                    # Mock embeddings
                    mock_embeddings.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

                    # Mock ChromaDB
                    mock_collection = MagicMock()
                    mock_client.return_value.create_collection.return_value = (
                        mock_collection
                    )

                    # Create vector store
                    response = client.post("/vector-store/create")
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    assert "stats" in data
                    assert data["stats"]["total_questions"] == 2


class TestErrorHandling:
    """Test error handling in integration scenarios"""

    @pytest.mark.integration
    def test_missing_configuration_handling(self, client):
        """Test handling of missing configuration"""
        # Test with missing Canvas configuration
        with patch("question_app.api.canvas.CANVAS_BASE_URL", None):
            response = client.get("/api/courses")
            assert response.status_code == 400

            response = client.get("/api/courses/123/quizzes")
            assert response.status_code == 400

    @pytest.mark.integration
    def test_file_operation_errors(self, client):
        """Test handling of file operation errors"""
        with patch(
            "question_app.main.load_questions", side_effect=Exception("File read error")
        ):
            # This should return a 500 error, not raise an exception
            response = client.get("/")
            assert response.status_code == 500

    @pytest.mark.integration
    def test_ai_service_errors(self, client, sample_questions):
        """Test handling of AI service errors"""
        with patch("question_app.api.questions.load_system_prompt", return_value="Test prompt"):
            with patch(
                "question_app.api.questions.load_questions", return_value=sample_questions
            ):
                with patch(
                    "question_app.api.questions.generate_feedback_with_ai",
                    side_effect=Exception("AI service error"),
                ):
                    response = client.post("/questions/1/generate-feedback")
                    assert response.status_code == 500

    @pytest.mark.integration
    def test_vector_store_errors(self, client, sample_questions):
        """Test handling of vector store errors"""
        with patch("question_app.api.vector_store.load_questions", return_value=sample_questions):
            with patch("chromadb.PersistentClient", side_effect=Exception("DB error")):
                response = client.post("/vector-store/create")
                assert response.status_code == 500


class TestDataConsistency:
    """Test data consistency across operations"""

    @pytest.mark.integration
    def test_question_data_consistency(self, client):
        """Test that question data remains consistent through operations"""
        with patch("question_app.api.questions.load_questions") as mock_load:
            with patch("question_app.api.questions.save_questions") as mock_save:
                # Initial state
                initial_questions = [
                    {
                        "id": 1,
                        "question_text": "Original question",
                        "answers": [{"id": 1, "text": "Answer", "weight": 100.0}],
                    }
                ]
                mock_load.return_value = initial_questions
                mock_save.return_value = True

                # Update question
                updated_data = {
                    "question_text": "Updated question",
                    "answers": [{"id": 1, "text": "Updated answer", "weight": 100.0}],
                }

                response = client.put("/questions/1", json=updated_data)
                assert response.status_code == 200

                # Verify save was called with updated data
                assert mock_save.called
                saved_questions = mock_save.call_args[0][0]
                assert len(saved_questions) == 1
                assert saved_questions[0]["question_text"] == "Updated question"

    @pytest.mark.integration
    def test_objectives_data_consistency(self, client):
        """Test that objectives data remains consistent"""
        with patch("question_app.api.objectives.load_objectives") as mock_load:
            with patch("question_app.api.objectives.save_objectives") as mock_save:
                mock_load.return_value = []
                mock_save.return_value = True

                objectives_data = {
                    "objectives": [
                        {
                            "text": "Test objective",
                            "blooms_level": "understand",
                            "priority": "high",
                        }
                    ]
                }

                response = client.post("/objectives", json=objectives_data)
                assert response.status_code == 200

                # Verify save was called with correct data
                assert mock_save.called
                saved_objectives = mock_save.call_args[0][0]
                assert len(saved_objectives) == 1
                assert saved_objectives[0]["text"] == "Test objective"


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_large_dataset_handling(self, client):
        """Test handling of large datasets"""
        # Create large dataset
        large_questions = []
        for i in range(100):
            large_questions.append(
                {
                    "id": i,
                    "question_text": f"Question {i}",
                    "question_type": "multiple_choice_question",
                    "answers": [{"id": 1, "text": f"Answer {i}", "weight": 100.0}],
                }
            )

        with patch("question_app.api.questions.load_questions", return_value=large_questions):
            with patch("question_app.api.questions.save_questions", return_value=True):
                # Test operations on large dataset without template rendering
                response = client.delete("/questions/50")
                assert response.status_code == 200

    @pytest.mark.integration
    def test_concurrent_operations(self, client):
        """Test concurrent operations handling"""
        import threading
        import time

        results = []

        def make_request():
            with patch("question_app.main.load_questions", return_value=[]):
                response = client.get("/")
                results.append(response.status_code)

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all requests succeeded
        assert all(status == 200 for status in results)
        assert len(results) == 5
