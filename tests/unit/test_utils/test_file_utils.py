"""
Unit tests for file utility functions
"""
import json
from unittest.mock import mock_open, patch

import pytest

from question_app.utils import (
    load_chat_system_prompt,
    load_objectives,
    load_questions,
    load_system_prompt,
    load_welcome_message,
    save_chat_system_prompt,
    save_objectives,
    save_questions,
    save_system_prompt,
    save_welcome_message,
)


class TestFileOperations:
    """
    Test file loading and saving operations.

    This test class covers all file I/O operations including loading and
    saving questions, objectives, and system prompts. It tests both
    successful operations and error handling scenarios.

    Test Coverage:
        - Loading from existing files
        - Loading from non-existent files
        - Saving data successfully
        - Error handling during file operations
        - JSON parsing and serialization
        - File encoding and formatting
    """

    @pytest.mark.unit
    def test_load_questions_empty_file(self):
        """Test loading questions from empty file"""
        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("os.path.exists", return_value=True):
                result = load_questions()
                assert result == []

    def test_load_questions_file_not_exists(self):
        """Test loading questions when file doesn't exist"""
        with patch("os.path.exists", return_value=False):
            result = load_questions()
            assert result == []

    def test_load_questions_with_data(self):
        """Test loading questions with actual data"""
        sample_data = [
            {"id": 1, "question_text": "Test question 1"},
            {"id": 2, "question_text": "Test question 2"},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_data))):
            with patch("os.path.exists", return_value=True):
                result = load_questions()
                assert result == sample_data

    def test_save_questions_success(self):
        """Test saving questions successfully"""
        questions = [{"id": 1, "question_text": "Test"}]
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_questions(questions)
            assert result is True
            mock_file.assert_called_once()

    def test_save_questions_failure(self):
        """Test saving questions with error"""
        questions = [{"id": 1, "question_text": "Test"}]
        with patch("builtins.open", side_effect=Exception("Write error")):
            result = save_questions(questions)
            assert result is False

    def test_load_objectives_empty_file(self):
        """Test loading objectives from empty file"""
        with patch("builtins.open", mock_open(read_data="[]")):
            with patch("os.path.exists", return_value=True):
                result = load_objectives()
                assert result == []

    def test_load_objectives_with_data(self):
        """Test loading objectives with actual data"""
        sample_data = [
            {"text": "Objective 1", "blooms_level": "understand"},
            {"text": "Objective 2", "blooms_level": "apply"},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_data))):
            with patch("os.path.exists", return_value=True):
                result = load_objectives()
                assert result == sample_data

    def test_save_objectives_success(self):
        """Test saving objectives successfully"""
        objectives = [{"text": "Test objective", "blooms_level": "understand"}]
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_objectives(objectives)
            assert result is True
            mock_file.assert_called_once()

    def test_load_system_prompt_empty_file(self):
        """Test loading system prompt from empty file"""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                result = load_system_prompt()
                assert result == ""

    def test_load_system_prompt_with_data(self):
        """Test loading system prompt with actual data"""
        prompt_data = "You are a helpful assistant for quiz questions."
        with patch("builtins.open", mock_open(read_data=prompt_data)):
            with patch("os.path.exists", return_value=True):
                result = load_system_prompt()
                assert result == prompt_data

    def test_save_system_prompt_success(self):
        """Test saving system prompt successfully"""
        prompt = "Test system prompt"
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_system_prompt(prompt)
            assert result is True
            mock_file.assert_called_once()

    def test_load_chat_system_prompt_empty_file(self):
        """Test loading chat system prompt from empty file"""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                result = load_chat_system_prompt()
                assert result == ""

    def test_load_chat_system_prompt_with_data(self):
        """Test loading chat system prompt with actual data"""
        prompt_data = "You are a helpful chat assistant."
        with patch("builtins.open", mock_open(read_data=prompt_data)):
            with patch("os.path.exists", return_value=True):
                result = load_chat_system_prompt()
                assert result == prompt_data

    def test_save_chat_system_prompt_success(self):
        """Test saving chat system prompt successfully"""
        prompt = "Test chat system prompt"
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_chat_system_prompt(prompt)
            assert result is True
            mock_file.assert_called_once()

    def test_load_welcome_message_empty_file(self):
        """Test loading welcome message from empty file"""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                result = load_welcome_message()
                assert result == ""

    def test_load_welcome_message_with_data(self):
        """Test loading welcome message with actual data"""
        message_data = "Welcome to the chat!"
        with patch("builtins.open", mock_open(read_data=message_data)):
            with patch("os.path.exists", return_value=True):
                result = load_welcome_message()
                assert result == message_data

    def test_save_welcome_message_success(self):
        """Test saving welcome message successfully"""
        message = "Test welcome message"
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_welcome_message(message)
            assert result is True
            mock_file.assert_called_once()
