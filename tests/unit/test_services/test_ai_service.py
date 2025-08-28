"""
Unit tests for AI service functions
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from question_app.services.ai_service import generate_feedback_with_ai


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

        with patch(
            "question_app.core.config.Config.validate_azure_openai_config",
            return_value=False,
        ):
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

    @pytest.mark.asyncio
    async def test_generate_feedback_invalid_response(self, sample_questions):
        """Test AI feedback generation with invalid response format"""
        question_data = sample_questions[0]
        system_prompt = "Test prompt"

        mock_ai_response = {
            "choices": [{"message": {"content": "Invalid response format"}}],
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

            # Should still return a result even with invalid format
            assert "general_feedback" in result
            assert "answer_feedback" in result
            assert "token_usage" in result
