"""
Text utility functions for the Canvas Quiz Manager.

This module contains functions for cleaning and processing text content,
including HTML cleaning, text normalization, and feedback processing.
"""

import re
from typing import List

from bs4 import BeautifulSoup


def clean_question_text(text: str) -> str:
    """
    Remove unwanted HTML tags from question text.

    This function specifically targets link, script, style, and meta tags that
    are commonly included in Canvas question text but are not relevant for
    display or processing.

    Args:
        text (str): The HTML text to clean.

    Returns:
        str: The cleaned text with unwanted HTML tags removed and whitespace normalized.

    Note:
        The function preserves the content within other HTML tags while removing
        only the specified unwanted tag types.
    """
    if not text:
        return text

    # Remove link tags (CSS files)
    text = re.sub(r"<link[^>]*?>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Remove script tags and their content
    text = re.sub(
        r"<script[^>]*?>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL
    )

    # Remove style tags and their content
    text = re.sub(
        r"<style[^>]*?>.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL
    )

    # Remove meta tags
    text = re.sub(r"<meta[^>]*?>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Clean up any extra whitespace that may have been left behind
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_html_for_vector_store(html_text: str) -> str:
    """
    Clean HTML tags and normalize text for vector store processing.

    This function extracts plain text from HTML content and normalizes whitespace
    to prepare text for embedding generation and vector storage.

    Args:
        html_text (str): The HTML text to clean and convert to plain text.

    Returns:
        str: The cleaned plain text with normalized whitespace.

    Note:
        This function uses BeautifulSoup to properly parse HTML and extract
        only the text content, removing all HTML markup.
    """
    if not html_text:
        return ""

    # Parse HTML and extract text
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text()

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_answer_feedback(feedback: str, answer_text: str = "") -> str:
    """
    Clean and format answer feedback text.

    This function processes feedback text to remove unwanted content and
    ensure it's properly formatted for display.

    Args:
        feedback (str): The feedback text to clean.
        answer_text (str): Optional answer text for context.

    Returns:
        str: The cleaned feedback text.

    Note:
        The function removes common unwanted patterns and normalizes whitespace.
    """
    if not feedback:
        return ""

    # Remove common unwanted patterns
    feedback = re.sub(r"Correct\.", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"Incorrect\.", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"Good job!", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"Try again\.", "", feedback, flags=re.IGNORECASE)

    # Remove weight indicators
    feedback = re.sub(r"\(Weight:\s*\d+%?\)", "", feedback, flags=re.IGNORECASE)

    # Remove correctness indicators
    feedback = re.sub(r"\[✓\s*CORRECT\]", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"\[✗\s*INCORRECT\]", "", feedback, flags=re.IGNORECASE)

    # Remove answer text prefix if provided
    if answer_text and feedback.startswith(f"{answer_text}:"):
        feedback = feedback[len(f"{answer_text}:") :].strip()
    elif answer_text and feedback.startswith(f"{answer_text} "):
        feedback = feedback[len(f"{answer_text} ") :].strip()

    # Clean up whitespace but preserve newlines
    feedback = re.sub(
        r"[ \t]+", " ", feedback
    )  # Replace multiple spaces/tabs with single space
    feedback = re.sub(
        r"\n\s*\n", "\n\n", feedback
    )  # Normalize multiple newlines to double newlines
    feedback = feedback.strip()

    return feedback


def get_all_existing_tags(questions: List[dict]) -> List[str]:
    """
    Extract all unique tags from a list of questions.

    Args:
        questions (List[dict]): List of question dictionaries.

    Returns:
        List[str]: List of unique tags found in the questions.

    Note:
        Tags are extracted from the 'tags' field and split by commas.
    """
    tags = set()
    for question in questions:
        if "tags" in question and question["tags"]:
            question_tags = [tag.strip() for tag in question["tags"].split(",")]
            tags.update(question_tags)
    return sorted(list(tags))


def extract_topic_from_text(text: str) -> str:
    """
    Extract a topic from text content.

    Args:
        text (str): The text to extract topic from.

    Returns:
        str: The extracted topic or 'general' if no topic found.

    Note:
        This is a simple implementation that could be enhanced with NLP.
    """
    if not text:
        return "general"

    # Simple keyword-based topic extraction
    text_lower = text.lower()

    # Accessibility keywords
    accessibility_keywords = [
        "accessibility",
        "screen reader",
        "alt text",
        "wcag",
        "aria",
        "accessible",
        "disability",
        "assistive",
    ]
    if any(word in text_lower for word in accessibility_keywords):
        return "accessibility"

    # Navigation keywords
    navigation_keywords = ["navigation", "menu", "nav", "breadcrumb", "sitemap"]
    if any(word in text_lower for word in navigation_keywords):
        return "navigation"

    # Forms keywords
    forms_keywords = ["form", "input", "label", "field", "submit", "validation"]
    if any(word in text_lower for word in forms_keywords):
        return "forms"

    # Media keywords
    media_keywords = ["video", "audio", "image", "caption", "transcript", "media"]
    if any(word in text_lower for word in media_keywords):
        return "media"

    # Keyboard keywords
    keyboard_keywords = ["keyboard", "shortcut", "tab", "focus", "arrow"]
    if any(word in text_lower for word in keyboard_keywords):
        return "keyboard"

    # Content keywords
    content_keywords = [
        "content",
        "semantic",
        "html",
        "structure",
        "heading",
        "element",
    ]
    if any(word in text_lower for word in content_keywords):
        return "content"

    return "general"
