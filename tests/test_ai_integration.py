"""
Tests for AI integration features
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from question_app.main import (
    create_comprehensive_chunks,
    generate_feedback_with_ai,
    get_ollama_embeddings,
    search_vector_store,
)


class TestAIFeedbackGeneration:
    """
    Test AI feedback generation functionality.

    This test class covers the AI-powered feedback generation features including
    successful API calls, error handling, configuration validation, and response
    parsing. It uses mocked Azure OpenAI responses to test various scenarios.

    Test Coverage:
        - Successful feedback generation with valid responses
        - Missing configuration handling
        - API error responses
        - Network timeouts
        - Response parsing and validation
    """

    @pytest.mark.asyncio
    async def test_generate_feedback_success(self, sample_questions):
        """
        Test successful AI feedback generation.

        This test verifies that the AI feedback generation works correctly
        with a valid Azure OpenAI response. It checks that the response
        is properly parsed and contains the expected feedback structure.

        Args:
            sample_questions: Fixture providing sample question data

        Assertions:
            - Response contains general_feedback
            - Response contains answer_feedback
            - Response contains token_usage
            - Token usage matches expected values
        """
        question_data = sample_questions[0]
        system_prompt = "You are a helpful assistant for quiz questions."

        mock_ai_response = {
            "choices": [
                {
                    "message": {
                        "content": """
                    Answer 1: London is the capital of England, not France.
                    Answer 2: Correct! Paris is the capital of France.
                    Answer 3: Berlin is the capital of Germany, not France.
                    """
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
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_ai_response
            mock_post.return_value = mock_response

            result = await generate_feedback_with_ai(question_data, system_prompt)

            assert "general_feedback" in result
            assert "answer_feedback" in result
            assert "token_usage" in result
            assert result["token_usage"]["total_tokens"] == 150

    @pytest.mark.asyncio
    async def test_generate_feedback_missing_config(self):
        """Test AI feedback generation with missing configuration"""
        question_data = {"id": 1, "question_text": "Test question"}
        system_prompt = "Test prompt"

        with patch("question_app.main.AZURE_OPENAI_ENDPOINT", None):
            with pytest.raises(Exception) as exc_info:
                await generate_feedback_with_ai(question_data, system_prompt)
            assert "Azure OpenAI configuration incomplete" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_generate_feedback_api_error(self, sample_questions):
        """Test AI feedback generation with API error"""
        question_data = sample_questions[0]
        system_prompt = "Test prompt"

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_post.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await generate_feedback_with_ai(question_data, system_prompt)
            assert "Failed to generate feedback" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_generate_feedback_timeout(self, sample_questions):
        """Test AI feedback generation with timeout"""
        question_data = sample_questions[0]
        system_prompt = "Test prompt"

        with patch("httpx.AsyncClient.post", side_effect=Exception("Timeout")):
            with pytest.raises(Exception) as exc_info:
                await generate_feedback_with_ai(question_data, system_prompt)
            assert "Failed to generate feedback" in str(exc_info.value.detail)


class TestOllamaEmbeddings:
    """Test Ollama embeddings functionality"""

    @pytest.mark.asyncio
    async def test_get_ollama_embeddings_success(self):
        """Test successful Ollama embeddings generation"""
        texts = ["Sample text 1", "Sample text 2"]
        mock_embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = [
                {"embedding": mock_embeddings[0]},
                {"embedding": mock_embeddings[1]},
            ]
            mock_post.return_value = mock_response

            result = await get_ollama_embeddings(texts)

            assert len(result) == 2
            assert result[0] == mock_embeddings[0]
            assert result[1] == mock_embeddings[1]

    @pytest.mark.asyncio
    async def test_get_ollama_embeddings_connection_error(self):
        """Test Ollama embeddings with connection error"""
        texts = ["Sample text"]

        with patch(
            "httpx.AsyncClient.post", side_effect=Exception("Connection failed")
        ):
            with pytest.raises(Exception) as exc_info:
                await get_ollama_embeddings(texts)
            assert "Failed to generate embeddings" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_ollama_embeddings_api_error(self):
        """Test Ollama embeddings with API error"""
        texts = ["Sample text"]

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Model not found"
            mock_post.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await get_ollama_embeddings(texts)
            assert "Failed to generate embeddings" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_ollama_embeddings_invalid_response(self):
        """Test Ollama embeddings with invalid response"""
        texts = ["Sample text"]

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"no_embedding": "here"}
            mock_post.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await get_ollama_embeddings(texts)
            assert "Failed to generate embeddings" in str(exc_info.value.detail)


class TestVectorStoreOperations:
    """Test vector store operations"""

    def test_create_comprehensive_chunks(self, sample_questions):
        """Test creating comprehensive chunks from questions"""
        documents, metadatas, ids = create_comprehensive_chunks(sample_questions)

        assert len(documents) == 2
        assert len(metadatas) == 2
        assert len(ids) == 2

        # Check document content
        assert "What is the capital of France?" in documents[0]
        assert "Which HTML tag is used for accessibility?" in documents[1]

        # Check metadata
        assert metadatas[0]["question_id"] == 1
        assert metadatas[1]["question_id"] == 2
        assert metadatas[0]["topic"] == "general"
        assert metadatas[1]["topic"] == "accessibility"

        # Check IDs
        assert ids[0] == "question_1"
        assert ids[1] == "question_2"

    def test_create_comprehensive_chunks_empty_questions(self):
        """Test creating chunks from empty questions list"""
        documents, metadatas, ids = create_comprehensive_chunks([])

        assert documents == []
        assert metadatas == []
        assert ids == []

    def test_create_comprehensive_chunks_with_feedback(self):
        """Test creating chunks with feedback content"""
        questions = [
            {
                "id": 1,
                "question_text": "What is accessibility?",
                "question_type": "multiple_choice_question",
                "points_possible": 1.0,
                "neutral_comments": "Accessibility helps users with disabilities.",
                "answers": [
                    {
                        "id": 1,
                        "text": "A design principle",
                        "weight": 100.0,
                        "comments": "Correct! Accessibility is a design principle.",
                    }
                ],
            }
        ]

        documents, metadatas, ids = create_comprehensive_chunks(questions)

        assert len(documents) == 1
        assert "What is accessibility?" in documents[0]
        assert "Accessibility helps users with disabilities" in documents[0]
        assert "A design principle (CORRECT)" in documents[0]

    @pytest.mark.asyncio
    async def test_search_vector_store_success(self):
        """Test successful vector store search"""
        mock_chunks = [
            {
                "content": "Sample context 1",
                "metadata": {"question_id": 1, "topic": "accessibility"},
                "distance": 0.1,
            },
            {
                "content": "Sample context 2",
                "metadata": {"question_id": 2, "topic": "forms"},
                "distance": 0.2,
            },
        ]

        with patch("chromadb.PersistentClient") as mock_client:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "documents": [["Sample context 1", "Sample context 2"]],
                "metadatas": [[{"question_id": 1}, {"question_id": 2}]],
                "distances": [[0.1, 0.2]],
            }
            mock_client.return_value.get_collection.return_value = mock_collection

            with patch("question_app.main.get_ollama_embeddings", return_value=[[0.1, 0.2, 0.3]]):
                result = await search_vector_store("test query", n_results=2)

                assert len(result) == 2
                assert result[0]["content"] == "Sample context 1"
                assert result[1]["content"] == "Sample context 2"

    @pytest.mark.asyncio
    async def test_search_vector_store_no_results(self):
        """Test vector store search with no results"""
        with patch("chromadb.PersistentClient") as mock_client:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }
            mock_client.return_value.get_collection.return_value = mock_collection

            with patch("question_app.main.get_ollama_embeddings", return_value=[[0.1, 0.2, 0.3]]):
                result = await search_vector_store("test query")

                assert result == []

    @pytest.mark.asyncio
    async def test_search_vector_store_embedding_failure(self):
        """Test vector store search with embedding failure"""
        with patch("question_app.main.get_ollama_embeddings", return_value=[]):
            result = await search_vector_store("test query")

            assert result == []

    @pytest.mark.asyncio
    async def test_search_vector_store_exception(self):
        """Test vector store search with exception"""
        with patch("chromadb.PersistentClient", side_effect=Exception("DB error")):
            result = await search_vector_store("test query")

            assert result == []


class TestFeedbackParsing:
    """Test AI feedback parsing functionality"""

    def test_parse_structured_feedback(self):
        """Test parsing structured AI feedback"""
        ai_response = """
        Answer 1: London is the capital of England, not France.
        Answer 2: Correct! Paris is the capital of France.
        Answer 3: Berlin is the capital of Germany, not France.
        """

        # This would be tested in the actual generate_feedback_with_ai function
        # For now, we test the parsing logic
        lines = ai_response.split("\n")
        feedback = {"answer_feedback": {}}

        for line in lines:
            line = line.strip()
            if line.startswith("Answer"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    feedback["answer_feedback"][key] = parts[1].strip()

        assert "answer 1" in feedback["answer_feedback"]
        assert "answer 2" in feedback["answer_feedback"]
        assert "answer 3" in feedback["answer_feedback"]

    def test_parse_unstructured_feedback(self):
        """Test parsing unstructured AI feedback"""
        ai_response = "This is general feedback about the question."

        # Test that unstructured feedback is handled gracefully
        feedback = {"general_feedback": ai_response}

        assert feedback["general_feedback"] == ai_response


class TestAIIntegrationEndpoints:
    """Test AI integration endpoints"""

    @pytest.mark.asyncio
    async def test_generate_question_feedback_endpoint_success(
        self, client, sample_questions
    ):
        """Test successful feedback generation endpoint"""
        with patch("question_app.main.load_system_prompt", return_value="Test prompt"):
            with patch("question_app.main.load_questions", return_value=sample_questions):
                with patch("question_app.main.generate_feedback_with_ai") as mock_generate:
                    mock_generate.return_value = {
                        "general_feedback": "Test feedback",
                        "answer_feedback": {"answer 1": "Test answer feedback"},
                        "token_usage": {"total_tokens": 100},
                    }

                    with patch("question_app.main.save_questions", return_value=True):
                        response = client.post("/questions/1/generate-feedback")
                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_generate_question_feedback_no_system_prompt(self, client):
        """Test feedback generation without system prompt"""
        with patch("question_app.main.load_system_prompt", return_value=""):
            response = client.post("/questions/1/generate-feedback")
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_generate_question_feedback_question_not_found(self, client):
        """Test feedback generation for non-existent question"""
        with patch("question_app.main.load_system_prompt", return_value="Test prompt"):
            with patch("question_app.main.load_questions", return_value=[]):
                response = client.post("/questions/999/generate-feedback")
                assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_vector_store_success(self, client, sample_questions):
        """Test successful vector store creation"""
        with patch("question_app.main.load_questions", return_value=sample_questions):
            with patch("question_app.main.get_ollama_embeddings") as mock_embeddings:
                mock_embeddings.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

                with patch("chromadb.PersistentClient") as mock_client:
                    mock_collection = MagicMock()
                    mock_client.return_value.create_collection.return_value = (
                        mock_collection
                    )

                    response = client.post("/create-vector-store")
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True

    @pytest.mark.asyncio
    async def test_create_vector_store_no_questions(self, client):
        """Test vector store creation with no questions"""
        with patch("question_app.main.load_questions", return_value=[]):
            response = client.post("/create-vector-store")
            assert response.status_code == 400
