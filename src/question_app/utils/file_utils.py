"""
File utility functions for the Canvas Quiz Manager.

This module contains functions for loading and saving data files
including questions, objectives, and configuration files.
"""

import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# File paths
DATA_FILE = "data/quiz_questions.json"
OBJECTIVES_FILE = "data/learning_objectives.json"
SYSTEM_PROMPT_FILE = "config/system_prompt.txt"
CHAT_SYSTEM_PROMPT_FILE = "config/chat_system_prompt.txt"
WELCOME_MESSAGE_FILE = "config/chat_welcome_message.txt"
FEEDBACK_PROMPT_CORRECT_FILE = "config/feedback_prompt_correct.txt"
FEEDBACK_PROMPT_INCORRECT_FILE = "config/feedback_prompt_incorrect.txt"
SYSTEM_PROMPTS_JSON = "data/system_prompts.json"


def load_questions() -> List[Dict[str, Any]]:
    """
    Load questions from the JSON data file.

    This function reads the quiz questions from the JSON data file and returns
    them as a list of dictionaries. It handles various error conditions gracefully
    including missing files, permission errors, and JSON parsing errors.

    Returns:
        List[Dict[str, Any]]: List of question dictionaries loaded from the file.
        Returns an empty list if the file doesn't exist or there's an error.

    Raises:
        No exceptions are raised. All errors are logged and handled gracefully.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
        If the file doesn't exist, an empty list is returned rather than an error.

    Example:
        >>> questions = load_questions()
        >>> print(f"Loaded {len(questions)} questions")
        Loaded 15 questions

        >>> # Handle empty file case
        >>> if not questions:
        ...     print("No questions found, starting with empty list")
        ...     questions = []
    """
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return []


def save_questions(questions: List[Dict[str, Any]]) -> bool:
    """
    Save questions to the JSON data file.

    This function writes the quiz questions to the JSON data file with proper
    formatting and error handling. It ensures the data is saved with UTF-8
    encoding and proper JSON formatting.

    Args:
        questions (List[Dict[str, Any]]): List of question dictionaries to save.

    Returns:
        bool: True if the save operation was successful, False otherwise.

    Raises:
        No exceptions are raised. All errors are logged and handled gracefully.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
        Data is saved with UTF-8 encoding and proper JSON formatting.

    Example:
        >>> sample_questions = [
        ...     {"id": 1, "question_text": "What is 2+2?", "answers": []},
        ...     {"id": 2, "question_text": "What is the capital of France?", "answers": []}
        ... ]
        >>> success = save_questions(sample_questions)
        >>> if success:
        ...     print("Questions saved successfully")
        ... else:
        ...     print("Failed to save questions")
        Questions saved successfully

    See Also:
        :func:`load_questions`: Load questions from the JSON file
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving questions: {e}")
        return False


def load_objectives() -> List[Dict[str, Any]]:
    """
    Load learning objectives from the JSON file.

    Returns:
        List[Dict[str, Any]]: List of learning objective dictionaries.
        Returns an empty list if the file doesn't exist or there's an error.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        if os.path.exists(OBJECTIVES_FILE):
            with open(OBJECTIVES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading objectives: {e}")
        return []


def save_objectives(objectives: List[Dict[str, Any]]) -> bool:
    """
    Save learning objectives to the JSON file.

    Args:
        objectives (List[Dict[str, Any]]): List of learning objective dictionaries.

    Returns:
        bool: True if the save operation was successful, False otherwise.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        with open(OBJECTIVES_FILE, "w", encoding="utf-8") as f:
            json.dump(objectives, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving objectives: {e}")
        return False


def load_system_prompt() -> str:
    """
    Load the system prompt from the text file.

    Returns:
        str: The system prompt content. Returns an empty string if the file
        doesn't exist or there's an error.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        if os.path.exists(SYSTEM_PROMPT_FILE):
            with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        return ""
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return ""


def save_system_prompt(prompt: str) -> bool:
    """
    Save the system prompt to the text file.

    Args:
        prompt (str): The system prompt content to save.

    Returns:
        bool: True if the save operation was successful, False otherwise.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        with open(SYSTEM_PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(prompt)
        return True
    except Exception as e:
        logger.error(f"Error saving system prompt: {e}")
        return False


def load_chat_system_prompt() -> str:
    """
    Load the chat system prompt from the text file.

    Returns:
        str: The chat system prompt content. Returns the default prompt if
        the file doesn't exist or there's an error.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        if os.path.exists(CHAT_SYSTEM_PROMPT_FILE):
            with open(CHAT_SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        return get_default_chat_system_prompt()
    except Exception as e:
        logger.error(f"Error loading chat system prompt: {e}")
        return get_default_chat_system_prompt()


def save_chat_system_prompt(prompt: str) -> bool:
    """
    Save the chat system prompt to the text file.

    Args:
        prompt (str): The chat system prompt content to save.

    Returns:
        bool: True if the save operation was successful, False otherwise.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        with open(CHAT_SYSTEM_PROMPT_FILE, "w", encoding="utf-8") as f:
            f.write(prompt)
        return True
    except Exception as e:
        logger.error(f"Error saving chat system prompt: {e}")
        return False


def load_welcome_message() -> str:
    """
    Load the chat welcome message from the text file.

    Returns:
        str: The welcome message content. Returns the default message if
        the file doesn't exist or there's an error.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        if os.path.exists(WELCOME_MESSAGE_FILE):
            with open(WELCOME_MESSAGE_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        return get_default_welcome_message()
    except Exception as e:
        logger.error(f"Error loading welcome message: {e}")
        return get_default_welcome_message()


def save_welcome_message(message: str) -> bool:
    """
    Save the chat welcome message to the text file.

    Args:
        message (str): The welcome message content to save.

    Returns:
        bool: True if the save operation was successful, False otherwise.

    Note:
        The function handles file I/O errors gracefully and logs any issues.
    """
    try:
        with open(WELCOME_MESSAGE_FILE, "w", encoding="utf-8") as f:
            f.write(message)
        return True
    except Exception as e:
        logger.error(f"Error saving welcome message: {e}")
        return False


def get_default_chat_system_prompt() -> str:
    """
    Get the default chat system prompt.

    Returns:
        str: The default chat system prompt text.
    """
    return """You are an intelligent educational assistant designed to help students and educators with Canvas LMS quiz questions. You have access to a comprehensive database of quiz questions and can provide detailed explanations, feedback, and guidance.

Your capabilities include:
- Analyzing quiz questions and providing detailed explanations
- Suggesting improvements to question wording and structure
- Providing educational feedback for different answer choices
- Helping with learning objectives and educational content
- Answering questions about Canvas LMS functionality

When providing responses, use the context from the quiz questions database to give accurate and relevant information. Always be helpful, educational, and supportive in your responses. Focus on learning outcomes and educational value."""


def load_feedback_prompt_correct() -> str:
    """
    Load the feedback prompt for correct answers.

    Returns:
        str: The feedback prompt for correct answers.
    """
    try:
        if os.path.exists(FEEDBACK_PROMPT_CORRECT_FILE):
            with open(FEEDBACK_PROMPT_CORRECT_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        return """You are an expert instructional designer. A student has selected the
CORRECT answer to a multiple-choice question.

Your task is to:
1.  Affirm that their answer is correct.
2.  Provide a detailed explanation (at least 4-5 sentences) of *why* this answer is correct.
3.  You should tie the concept back to the core learning objective.

Respond *only* with the feedback text. Do not add any extra titles or "Feedback:" prefix."""
    except Exception as e:
        logger.error(f"Error loading correct feedback prompt: {e}")
        return ""


def save_feedback_prompt_correct(prompt: str) -> bool:
    """
    Save the feedback prompt for correct answers.

    Args:
        prompt (str): The feedback prompt content to save.

    Returns:
        bool: True if the save operation was successful, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(FEEDBACK_PROMPT_CORRECT_FILE), exist_ok=True)
        with open(FEEDBACK_PROMPT_CORRECT_FILE, "w", encoding="utf-8") as f:
            f.write(prompt)
        return True
    except Exception as e:
        logger.error(f"Error saving correct feedback prompt: {e}")
        return False


def load_feedback_prompt_incorrect() -> str:
    """
    Load the feedback prompt for incorrect answers.

    Returns:
        str: The feedback prompt for incorrect answers.
    """
    try:
        if os.path.exists(FEEDBACK_PROMPT_INCORRECT_FILE):
            with open(FEEDBACK_PROMPT_INCORRECT_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        return """You are an expert instructional designer. A student has selected the
INCORRECT answer to a multiple-choice question.

Your task is to:
1.  Affirm that their answer is incorrect.
2.  Generate one (1) probing socratic questions (2-3 sentences) that gently guides them to reconsider their choice.
3.  Your question should make them think about the *concept* that makes their answers incorrect.

Respond *only* with the feedback text. Do not add any extra titles or "Feedback:" prefix."""
    except Exception as e:
        logger.error(f"Error loading incorrect feedback prompt: {e}")
        return ""


def save_feedback_prompt_incorrect(prompt: str) -> bool:
    """
    Save the feedback prompt for incorrect answers.

    Args:
        prompt (str): The feedback prompt content to save.

    Returns:
        bool: True if the save operation was successful, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(FEEDBACK_PROMPT_INCORRECT_FILE), exist_ok=True)
        with open(FEEDBACK_PROMPT_INCORRECT_FILE, "w", encoding="utf-8") as f:
            f.write(prompt)
        return True
    except Exception as e:
        logger.error(f"Error saving incorrect feedback prompt: {e}")
        return False


def get_default_welcome_message() -> str:
    """
    Get the default chat welcome message.

    Returns:
        str: The default welcome message text.
    """
    return """Welcome to the Canvas Quiz Manager Chat Assistant! 

I'm here to help you with:
- Understanding quiz questions and concepts
- Getting feedback on your answers
- Learning about educational content
- Improving your study strategies

Feel free to ask me anything about the quiz questions or educational content. I'm here to support your learning journey!"""



def load_feedback_prompt_from_json(prompt_type: str) -> str:
    """Generic loader for feedback prompts (correct/incorrect) from a single JSON file."""
    try:
        if os.path.exists(SYSTEM_PROMPTS_JSON):
            with open(SYSTEM_PROMPTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(prompt_type, "").strip()
        return ""
    except Exception as e:
        logger.error(f"Error loading feedback prompt ({prompt_type}): {e}")
        return ""


def save_feedback_prompt_to_json(prompt_type: str, prompt_text: str) -> bool:
    """Generic saver for feedback prompts to a single JSON file."""
    try:
        os.makedirs(os.path.dirname(SYSTEM_PROMPTS_JSON), exist_ok=True)
        data = {}
        if os.path.exists(SYSTEM_PROMPTS_JSON):
            with open(SYSTEM_PROMPTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
        data[prompt_type] = prompt_text
        with open(SYSTEM_PROMPTS_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving feedback prompt ({prompt_type}): {e}")
        return False