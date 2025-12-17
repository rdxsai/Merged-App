"""
Utilities package for the Question App.

This package contains utility functions, helpers, and common
functionality used across the application.
"""

from .file_utils import (
    get_default_chat_system_prompt,
    get_default_welcome_message,
    load_chat_system_prompt,
    load_feedback_prompt_correct,
    load_feedback_prompt_incorrect,
    load_objectives,
    load_questions,
    load_system_prompt,
    load_welcome_message,
    save_chat_system_prompt,
    save_feedback_prompt_correct,
    save_feedback_prompt_incorrect,
    save_objectives,
    save_questions,
    save_system_prompt,
    save_welcome_message,
)
from .text_utils import (
    clean_answer_feedback,
    clean_html_for_vector_store,
    clean_question_text,
    extract_topic_from_text,
    get_all_existing_tags,
)

from .file_utils import (
    load_feedback_prompt_from_json,
    save_feedback_prompt_to_json,
)

__all__ = [
    # File utilities
    "load_questions",
    "save_questions",
    "load_objectives",
    "save_objectives",
    "load_system_prompt",
    "save_system_prompt",
    "load_chat_system_prompt",
    "save_chat_system_prompt",
    "load_welcome_message",
    "save_welcome_message",
    "get_default_chat_system_prompt",
    "get_default_welcome_message",
    # Text utilities
    "clean_question_text",
    "clean_html_for_vector_store",
    "clean_answer_feedback",
    "get_all_existing_tags",
    "extract_topic_from_text",
]
