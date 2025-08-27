"""
Unit tests for utility functions
"""
import json
import os
import tempfile
from unittest.mock import mock_open, patch

import pytest

from question_app.main import (
    clean_answer_feedback,
    clean_html_for_vector_store,
    clean_question_text,
    extract_topic_from_text,
    get_all_existing_tags,
    get_default_chat_system_prompt,
    get_default_welcome_message,
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

    def test_load_system_prompt_empty_file(self):
        """Test loading system prompt from empty file"""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                result = load_system_prompt()
                assert result == ""

    def test_load_system_prompt_with_content(self):
        """Test loading system prompt with content"""
        prompt_content = "You are a helpful assistant."
        with patch("builtins.open", mock_open(read_data=prompt_content)):
            with patch("os.path.exists", return_value=True):
                result = load_system_prompt()
                assert result == prompt_content

    def test_save_system_prompt_success(self):
        """Test saving system prompt successfully"""
        prompt = "Test system prompt"
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_system_prompt(prompt)
            assert result is True


class TestTextCleaning:
    """Test text cleaning and processing functions"""

    @pytest.mark.unit
    def test_clean_question_text_empty(self):
        """Test cleaning empty question text"""
        result = clean_question_text("")
        assert result == ""

    def test_clean_question_text_none(self):
        """Test cleaning None question text"""
        result = clean_question_text(None)
        assert result is None

    def test_clean_question_text_remove_links(self):
        """Test removing link tags from question text"""
        text = '<link rel="stylesheet" href="style.css">What is the capital?'
        result = clean_question_text(text)
        assert "link" not in result
        assert "What is the capital?" in result

    def test_clean_question_text_remove_scripts(self):
        """Test removing script tags from question text"""
        text = '<script>alert("test");</script>What is the capital?'
        result = clean_question_text(text)
        assert "script" not in result
        assert "alert" not in result
        assert "What is the capital?" in result

    def test_clean_question_text_remove_styles(self):
        """Test removing style tags from question text"""
        text = "<style>body { color: red; }</style>What is the capital?"
        result = clean_question_text(text)
        assert "style" not in result
        assert "color: red" not in result
        assert "What is the capital?" in result

    def test_clean_html_for_vector_store_empty(self):
        """Test cleaning empty HTML for vector store"""
        result = clean_html_for_vector_store("")
        assert result == ""

    def test_clean_html_for_vector_store_with_html(self):
        """Test cleaning HTML for vector store"""
        html = "<p>This is a <strong>test</strong> question.</p>"
        result = clean_html_for_vector_store(html)
        assert result == "This is a test question."

    def test_clean_html_for_vector_store_complex(self):
        """Test cleaning complex HTML for vector store"""
        html = """
        <div class="question">
            <h2>Question Title</h2>
            <p>This is the <em>question</em> text with <a href="#">links</a>.</p>
        </div>
        """
        result = clean_html_for_vector_store(html)
        assert "Question Title" in result
        assert "This is the question text with links." in result
        assert "<" not in result  # No HTML tags should remain


class TestTopicExtraction:
    """Test topic extraction functionality"""

    def test_extract_topic_accessibility(self):
        """Test extracting accessibility topic"""
        text = "What is the best practice for screen reader accessibility?"
        result = extract_topic_from_text(text)
        assert result == "accessibility"

    def test_extract_topic_navigation(self):
        """Test extracting navigation topic"""
        text = "How should you implement navigation menus?"
        result = extract_topic_from_text(text)
        assert result == "navigation"

    def test_extract_topic_forms(self):
        """Test extracting forms topic"""
        text = "What is the proper way to label form inputs?"
        result = extract_topic_from_text(text)
        assert result == "forms"

    def test_extract_topic_media(self):
        """Test extracting media topic"""
        text = "How do you add captions to videos?"
        result = extract_topic_from_text(text)
        assert result == "media"

    def test_extract_topic_media_with_images(self):
        """Test extracting media topic for image-related content"""
        text = "What is the best way to handle image optimization?"
        result = extract_topic_from_text(text)
        assert result == "media"

    def test_extract_topic_media_with_audio(self):
        """Test extracting media topic for audio content"""
        text = "How do you provide transcripts for audio files?"
        result = extract_topic_from_text(text)
        assert result == "media"

    def test_extract_topic_media_accessibility_overlap(self):
        """Test that accessibility keywords take precedence over media for alt text"""
        text = "How do you make images accessible with alt text?"
        result = extract_topic_from_text(text)
        # This should return "accessibility" because "alt text" is in accessibility keywords
        assert result == "accessibility"

    def test_extract_topic_keyboard(self):
        """Test extracting keyboard topic"""
        text = "How do you implement keyboard shortcuts?"
        result = extract_topic_from_text(text)
        assert result == "keyboard"

    def test_extract_topic_content(self):
        """Test extracting content topic"""
        text = "What are semantic HTML elements?"
        result = extract_topic_from_text(text)
        assert result == "content"

    def test_extract_topic_general(self):
        """Test extracting general topic for unknown content"""
        text = "What is the weather like today?"
        result = extract_topic_from_text(text)
        assert result == "general"

    def test_extract_topic_with_feedback(self):
        """Test extracting topic with feedback text"""
        question = "What is accessibility?"
        feedback = "This relates to screen readers and WCAG guidelines."
        result = extract_topic_from_text(question, feedback)
        assert result == "accessibility"


class TestAnswerFeedbackCleaning:
    """Test answer feedback cleaning functionality"""

    def test_clean_answer_feedback_empty(self):
        """Test cleaning empty feedback"""
        result = clean_answer_feedback("")
        assert result == ""

    def test_clean_answer_feedback_remove_weight(self):
        """Test removing weight indicators from feedback"""
        feedback = "This is correct (Weight: 100%)"
        result = clean_answer_feedback(feedback)
        assert "(Weight: 100%)" not in result
        assert "This is correct" in result

    def test_clean_answer_feedback_remove_correctness_indicators(self):
        """Test removing correctness indicators from feedback"""
        feedback = "[✓ CORRECT] This is the right answer"
        result = clean_answer_feedback(feedback)
        assert "[✓ CORRECT]" not in result
        assert "This is the right answer" in result

    def test_clean_answer_feedback_remove_answer_text(self):
        """Test removing answer text from feedback"""
        answer_text = "Paris"
        feedback = "Paris: This is the capital of France"
        result = clean_answer_feedback(feedback, answer_text)
        assert "Paris:" not in result
        assert "This is the capital of France" in result

    def test_clean_answer_feedback_complex(self):
        """Test cleaning complex feedback with multiple elements"""
        answer_text = "Paris"
        feedback = "Paris (Weight: 100%) [✓ CORRECT]: This is the capital of France"
        result = clean_answer_feedback(feedback, answer_text)
        assert "Paris" not in result
        assert "(Weight: 100%)" not in result
        assert "[✓ CORRECT]" not in result
        assert "This is the capital of France" in result


class TestTagExtraction:
    """Test tag extraction functionality"""

    def test_get_all_existing_tags_empty(self):
        """Test getting tags from empty questions list"""
        questions = []
        result = get_all_existing_tags(questions)
        assert result == []

    def test_get_all_existing_tags_no_tags(self):
        """Test getting tags from questions with no tags"""
        questions = [
            {"id": 1, "question_text": "Test question 1"},
            {"id": 2, "question_text": "Test question 2"},
        ]
        result = get_all_existing_tags(questions)
        assert result == []

    def test_get_all_existing_tags_single_tag(self):
        """Test getting tags from questions with single tags"""
        questions = [{"id": 1, "tags": "accessibility"}, {"id": 2, "tags": "html"}]
        result = get_all_existing_tags(questions)
        assert result == ["accessibility", "html"]

    def test_get_all_existing_tags_multiple_tags(self):
        """Test getting tags from questions with multiple tags"""
        questions = [
            {"id": 1, "tags": "accessibility,html,wcag"},
            {"id": 2, "tags": "forms,validation,html"},
        ]
        result = get_all_existing_tags(questions)
        expected = ["accessibility", "forms", "html", "validation", "wcag"]
        assert result == expected

    def test_get_all_existing_tags_duplicate_tags(self):
        """Test getting tags with duplicates"""
        questions = [
            {"id": 1, "tags": "accessibility,html"},
            {"id": 2, "tags": "html,forms"},
            {"id": 3, "tags": "accessibility,forms"},
        ]
        result = get_all_existing_tags(questions)
        expected = ["accessibility", "forms", "html"]
        assert result == expected

    def test_get_all_existing_tags_with_whitespace(self):
        """Test getting tags with whitespace"""
        questions = [
            {"id": 1, "tags": "accessibility , html , wcag"},
            {"id": 2, "tags": "forms, validation , html"},
        ]
        result = get_all_existing_tags(questions)
        expected = ["accessibility", "forms", "html", "validation", "wcag"]
        assert result == expected


class TestChatUtilityFunctions:
    """Test chat-related utility functions"""

    def test_load_chat_system_prompt_empty_file(self):
        """Test loading chat system prompt from empty file"""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                result = load_chat_system_prompt()
                assert result == ""

    def test_load_chat_system_prompt_with_content(self):
        """Test loading chat system prompt with content"""
        prompt_content = "You are a helpful chat assistant."
        with patch("builtins.open", mock_open(read_data=prompt_content)):
            with patch("os.path.exists", return_value=True):
                result = load_chat_system_prompt()
                assert result == prompt_content

    def test_load_chat_system_prompt_file_not_exists(self):
        """Test loading chat system prompt when file doesn't exist"""
        with patch("os.path.exists", return_value=False):
            result = load_chat_system_prompt()
            # Should return default prompt when file doesn't exist
            assert isinstance(result, str)
            assert len(result) > 0

    def test_save_chat_system_prompt_success(self):
        """Test saving chat system prompt successfully"""
        prompt = "Test chat system prompt"
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_chat_system_prompt(prompt)
            assert result is True
            mock_file.assert_called_once()

    def test_save_chat_system_prompt_failure(self):
        """Test saving chat system prompt with error"""
        prompt = "Test chat system prompt"
        with patch("builtins.open", side_effect=Exception("Write error")):
            result = save_chat_system_prompt(prompt)
            assert result is False

    def test_get_default_chat_system_prompt(self):
        """Test getting default chat system prompt"""
        result = get_default_chat_system_prompt()
        assert isinstance(result, str)
        assert len(result) > 0
        assert "context" in result  # Should contain context placeholder

    def test_load_welcome_message_empty_file(self):
        """Test loading welcome message from empty file"""
        with patch("builtins.open", mock_open(read_data="")):
            with patch("os.path.exists", return_value=True):
                result = load_welcome_message()
                assert result == ""

    def test_load_welcome_message_with_content(self):
        """Test loading welcome message with content"""
        message_content = "Welcome to the chat assistant!"
        with patch("builtins.open", mock_open(read_data=message_content)):
            with patch("os.path.exists", return_value=True):
                result = load_welcome_message()
                assert result == message_content

    def test_load_welcome_message_file_not_exists(self):
        """Test loading welcome message when file doesn't exist"""
        with patch("os.path.exists", return_value=False):
            result = load_welcome_message()
            # Should return default message when file doesn't exist
            assert isinstance(result, str)
            assert len(result) > 0

    def test_save_welcome_message_success(self):
        """Test saving welcome message successfully"""
        message = "Test welcome message"
        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            result = save_welcome_message(message)
            assert result is True
            mock_file.assert_called_once()

    def test_save_welcome_message_failure(self):
        """Test saving welcome message with error"""
        message = "Test welcome message"
        with patch("builtins.open", side_effect=Exception("Write error")):
            result = save_welcome_message(message)
            assert result is False

    def test_get_default_welcome_message(self):
        """Test getting default welcome message"""
        result = get_default_welcome_message()
        assert isinstance(result, str)
        assert len(result) > 0
        assert "assistant" in result.lower()  # Should mention assistant functionality
