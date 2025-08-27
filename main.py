"""
Canvas Quiz Manager - A Comprehensive Web Application

This module provides a FastAPI-based web application for managing Canvas LMS quiz
questions with AI-powered feedback generation and an intelligent chat assistant
using RAG (Retrieval-Augmented Generation).

The application integrates with:
- Canvas LMS API for fetching quiz questions
- Azure OpenAI for AI-powered feedback generation
- Ollama for local embedding generation
- ChromaDB for vector storage and semantic search
- FastAPI for web API and frontend

Key Features:
- Fetch and manage quiz questions from Canvas LMS
- Generate educational feedback using AI
- Intelligent chat assistant with RAG capabilities
- Vector store for semantic search
- Learning objectives management
- System prompt customization

Author: Bryce Kayanuma <BrycePK@vt.edu>
Version: 0.1.0
"""

import asyncio
import json
import logging
import os
import random
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import chromadb
import httpx
import uvicorn
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# TODO: Test fastapi_mpc https://github.com/tadata-org/fastapi_mcp
# TODO: Offload vector store to S3 Vector Bucket

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("canvas_app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Canvas Quiz Manager")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configuration from environment
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
COURSE_ID = os.getenv("COURSE_ID")
QUIZ_ID = os.getenv("QUIZ_ID")

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT", "https://itls-openai-connect.azure-api.net"
)
AZURE_OPENAI_DEPLOYMENT_ID = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
AZURE_OPENAI_SUBSCRIPTION_KEY = os.getenv("AZURE_OPENAI_SUBSCRIPTION_KEY")

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# File paths
DATA_FILE = "quiz_questions.json"
SYSTEM_PROMPT_FILE = "system_prompt.txt"
CHAT_SYSTEM_PROMPT_FILE = "chat_system_prompt.txt"
WELCOME_MESSAGE_FILE = "chat_welcome_message.txt"


# Pydantic models
class Answer(BaseModel):
    """
    Pydantic model representing a quiz answer option.

    Attributes:
        id (int): Unique identifier for the answer
        text (str): The answer text content
        html (str): HTML formatted version of the answer text
        comments (str): Feedback comments for this answer
        comments_html (str): HTML formatted version of the comments
        weight (float): Weight/score for this answer (0-100)
    """

    id: int
    text: str
    html: str = ""
    comments: str = ""
    comments_html: str = ""
    weight: float = 0.0


class Question(BaseModel):
    """
    Pydantic model representing a complete quiz question.

    Attributes:
        id (int): Unique identifier for the question
        quiz_id (int): ID of the quiz this question belongs to
        question_name (str): Name/title of the question
        question_type (str): Type of question (e.g., 'multiple_choice_question')
        question_text (str): The main question text
        points_possible (float): Maximum points for this question
        correct_comments (str): Feedback shown when answer is correct
        incorrect_comments (str): Feedback shown when answer is incorrect
        neutral_comments (str): General feedback for the question
        correct_comments_html (str): HTML formatted correct comments
        incorrect_comments_html (str): HTML formatted incorrect comments
        neutral_comments_html (str): HTML formatted neutral comments
        answers (List[Answer]): List of answer options for this question
    """

    id: int
    quiz_id: int
    question_name: str
    question_type: str
    question_text: str
    points_possible: float
    correct_comments: str = ""
    incorrect_comments: str = ""
    neutral_comments: str = ""
    correct_comments_html: str = ""
    incorrect_comments_html: str = ""
    neutral_comments_html: str = ""
    answers: List[Answer] = []


class QuestionUpdate(BaseModel):
    """
    Pydantic model for updating existing questions.

    Attributes:
        question_text (str): Updated question text
        topic (str): Topic/category for the question
        tags (str): Comma-separated tags for the question
        learning_objective (str): Associated learning objective
        correct_comments (str): Feedback for correct answers
        incorrect_comments (str): Feedback for incorrect answers
        neutral_comments (str): General feedback
        correct_comments_html (str): HTML formatted correct comments
        incorrect_comments_html (str): HTML formatted incorrect comments
        neutral_comments_html (str): HTML formatted neutral comments
        answers (List[Answer]): Updated list of answer options
    """

    question_text: str
    topic: str = "general"
    tags: str = ""
    learning_objective: str = ""
    correct_comments: str = ""
    incorrect_comments: str = ""
    neutral_comments: str = ""
    correct_comments_html: str = ""
    incorrect_comments_html: str = ""
    neutral_comments_html: str = ""
    answers: List[Answer] = []


class LearningObjective(BaseModel):
    """
    Pydantic model representing a learning objective.

    Attributes:
        text (str): The learning objective text
        blooms_level (str): Bloom's taxonomy level (e.g., 'understand')
        priority (str): Priority level ('low', 'medium', 'high')
    """

    text: str
    blooms_level: str = "understand"
    priority: str = "medium"


class ObjectivesUpdate(BaseModel):
    """
    Pydantic model for updating learning objectives.

    Attributes:
        objectives (List[LearningObjective]): List of learning objectives
    """

    objectives: List[LearningObjective] = []


class NewQuestion(BaseModel):
    """
    Pydantic model for creating new questions.

    Attributes:
        question_text (str): The question text
        question_type (str): Type of question
        topic (str): Topic/category for the question
        tags (str): Comma-separated tags
        learning_objective (str): Associated learning objective
        points_possible (float): Maximum points for the question
        neutral_comments (str): General feedback
        answers (List[Answer]): List of answer options
    """

    question_text: str
    question_type: str = "multiple_choice_question"
    topic: str = "general"
    tags: str = ""
    learning_objective: str = ""
    points_possible: float = 1.0
    neutral_comments: str = ""
    answers: List[Answer] = []


# Utility functions
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
        objectives_file = "learning_objectives.json"
        if os.path.exists(objectives_file):
            with open(objectives_file, "r", encoding="utf-8") as f:
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
        objectives_file = "learning_objectives.json"
        with open(objectives_file, "w", encoding="utf-8") as f:
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


def get_default_chat_system_prompt() -> str:
    """
    Get the default chat system prompt template.

    Returns:
        str: The default system prompt template for the chat assistant.
        This prompt includes placeholders for context injection.
    """
    return """You are a helpful assistant specializing in web accessibility and quiz questions. 
You have access to a knowledge base of quiz questions about accessibility topics.

Use the following context to answer the user's question. If the context doesn't contain relevant information, 
you can still provide general knowledge about accessibility and web development best practices.

Context from knowledge base:
{context}

Instructions:
- Be helpful and informative
- Focus on accessibility and educational content
- If referencing specific questions, mention the question ID when available
- Keep responses concise but thorough
- If you don't know something, say so rather than making up information
- Provide practical examples when possible
- Reference WCAG guidelines when relevant"""


def load_welcome_message() -> str:
    """
    Load the welcome message from the text file.

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
    Save the welcome message to the text file.

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


def get_default_welcome_message() -> str:
    """
    Get the default welcome message for the chat assistant.

    Returns:
        str: The default welcome message that introduces the chat assistant
        and explains its capabilities.
    """
    return "Hi! I'm your quiz assistant. I can help you with questions about accessibility, quiz content, and best practices. Ask me anything about the quiz questions in your knowledge base!"


async def make_canvas_request(
    url: str, headers: Dict[str, str], max_retries: int = 3
) -> Dict[str, Any]:
    """
    Make a Canvas API request with retry logic for rate limiting.

    Args:
        url (str): The Canvas API endpoint URL to request.
        headers (Dict[str, str]): HTTP headers to include in the request.
        max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.

    Returns:
        Dict[str, Any]: JSON response from the Canvas API.

    Raises:
        HTTPException: If the request fails after all retry attempts or if
                      the API returns an error status code.

    Note:
        This function implements exponential backoff for rate limiting (429 errors)
        and includes proper error handling for various HTTP status codes.
    """
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 429:  # Rate limited
                    wait_time = 2**attempt + random.uniform(0, 1)
                    logger.warning(
                        f"Rate limited, waiting {wait_time:.2f} seconds before retry {attempt + 1}"
                    )
                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=e.response.status_code, detail=f"Canvas API error: {e}"
                )
        except Exception as e:
            logger.error(f"Request error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"Request failed: {e}")

    raise HTTPException(status_code=500, detail="Max retries exceeded")


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


async def get_ollama_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings from Ollama using the nomic-embed-text model.

    This function generates vector embeddings for a list of text inputs using
    the local Ollama service with the nomic-embed-text model. It handles
    connection management, error handling, and request throttling automatically.

    Args:
        texts (List[str]): List of text strings to generate embeddings for.
                          Empty strings are allowed but will result in zero vectors.

    Returns:
        List[List[float]]: List of embedding vectors, where each vector is a
        list of floats representing the text in high-dimensional space.
        Returns empty list if all requests fail.

    Raises:
        HTTPException: If there are connection issues, timeouts, or API errors
                      with the Ollama service.

    Note:
        The function includes a small delay between requests to avoid overwhelming
        the Ollama service. It also handles various error conditions including
        connection failures, timeouts, and invalid responses.

    Example:
        >>> texts = [
        ...     "What is the capital of France?",
        ...     "Explain the concept of accessibility in web design"
        ... ]
        >>> embeddings = await get_ollama_embeddings(texts)
        >>> print(f"Generated {len(embeddings)} embeddings")
        >>> print(f"Each embedding has {len(embeddings[0])} dimensions")
        Generated 2 embeddings
        Each embedding has 768 dimensions

    See Also:
        :func:`search_vector_store`: Use embeddings for semantic search
        :func:`create_comprehensive_chunks`: Prepare text for embedding
    """
    embeddings = []

    # Ensure OLLAMA_HOST has proper protocol
    ollama_host = OLLAMA_HOST
    if not ollama_host.startswith(("http://", "https://")):
        ollama_host = f"http://{ollama_host}"

    logger.info(f"Using Ollama host: {ollama_host}")
    logger.info(f"Using embedding model: {OLLAMA_EMBEDDING_MODEL}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            for i, text in enumerate(texts):
                payload = {"model": OLLAMA_EMBEDDING_MODEL, "prompt": text}

                logger.info(
                    f"Generating embedding {i+1}/{len(texts)} (text length: {len(text)} chars)"
                )

                url = f"{ollama_host}/api/embeddings"
                logger.debug(f"Making request to: {url}")

                response = await client.post(
                    url, json=payload, headers={"Content-Type": "application/json"}
                )

                if response.status_code != 200:
                    error_text = response.text
                    logger.error(
                        f"Ollama API error (status {response.status_code}): {error_text}"
                    )
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Ollama API error: {error_text}",
                    )

                result = response.json()

                if "embedding" not in result:
                    logger.error(f"No embedding in Ollama response: {result}")
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid response from Ollama - no embedding found",
                    )

                embeddings.append(result["embedding"])

                # Add small delay to avoid overwhelming Ollama
                await asyncio.sleep(0.1)

        logger.info(
            f"Generated {len(embeddings)} embeddings using Ollama {OLLAMA_EMBEDDING_MODEL} model"
        )
        return embeddings

    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to Ollama at {ollama_host}: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama at {ollama_host}. Please ensure Ollama is running and the {OLLAMA_EMBEDDING_MODEL} model is installed.",
        )
    except httpx.TimeoutException as e:
        logger.error(f"Ollama request timeout: {e}")
        raise HTTPException(status_code=408, detail="Ollama request timed out")
    except Exception as e:
        logger.error(f"Error generating embeddings with Ollama: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate embeddings: {str(e)}"
        )


def create_comprehensive_chunks(
    questions: List[Dict[str, Any]]
) -> tuple[List[str], List[Dict[str, Any]], List[str]]:
    """
    Create comprehensive chunks from quiz questions for vector store processing.

    This function transforms quiz questions into comprehensive text chunks that
    include question text, answer options, feedback, and metadata. The chunks
    are designed to provide rich context for semantic search and RAG operations.

    Args:
        questions (List[Dict[str, Any]]): List of question dictionaries to process.

    Returns:
        tuple[List[str], List[Dict[str, Any]], List[str]]: A tuple containing:
            - List of document texts (the chunks)
            - List of metadata dictionaries for each chunk
            - List of unique IDs for each chunk

    Note:
        The function creates comprehensive chunks that include:
        - Question text and type
        - All answer options with correctness indicators
        - General feedback and answer-specific feedback
        - Rich metadata for filtering and analysis
    """
    documents = []
    metadatas = []
    ids = []

    for question in questions:
        # Extract and clean question text
        question_text = clean_html_for_vector_store(question.get("question_text", ""))
        question_type = question.get("question_type", "")
        general_feedback = clean_html_for_vector_store(
            question.get("neutral_comments", "")
        )

        # Build comprehensive document text
        doc_parts = []

        # Add question
        if question_text:
            doc_parts.append(f"Question: {question_text}")

        # Add question type context
        if question_type:
            doc_parts.append(
                f"Question Type: {question_type.replace('_', ' ').title()}"
            )

        # Process answers
        correct_answers = []
        all_answers = []
        answer_feedback_parts = []

        for answer in question.get("answers", []):
            answer_text = clean_html_for_vector_store(answer.get("text", ""))
            weight = answer.get("weight", 0)
            is_correct = weight > 0
            answer_feedback = clean_html_for_vector_store(answer.get("comments", ""))

            if answer_text:
                status = "CORRECT" if is_correct else "INCORRECT"
                all_answers.append(f"- {answer_text} ({status})")

                if is_correct:
                    correct_answers.append(answer_text)

                # Add specific answer feedback if available
                if answer_feedback:
                    answer_feedback_parts.append(
                        f"Feedback for '{answer_text}': {answer_feedback}"
                    )

        # Combine all answers
        if all_answers:
            doc_parts.append("Answer Options:\n" + "\n".join(all_answers))

        # Add general feedback
        if general_feedback:
            doc_parts.append(f"General Explanation: {general_feedback}")

        # Add answer-specific feedback
        if answer_feedback_parts:
            doc_parts.append("Answer Feedback:\n" + "\n".join(answer_feedback_parts))

        # Create final document
        document_text = "\n\n".join(doc_parts)

        # Create metadata (ChromaDB only accepts str, int, float, bool, or None)
        metadata = {
            "question_id": question.get("id"),
            "question_type": question_type,
            "points_possible": float(question.get("points_possible", 0)),
            "correct_answers": " | ".join(correct_answers)
            if correct_answers
            else "",  # Convert list to string
            "answer_count": len(question.get("answers", [])),
            "has_feedback": bool(general_feedback),
            "topic": question.get(
                "topic", extract_topic_from_text(question_text, general_feedback)
            ),
            "tags": question.get("tags", ""),
            "learning_objective": question.get("learning_objective", ""),
        }

        documents.append(document_text)
        metadatas.append(metadata)
        ids.append(f"question_{question.get('id')}")

    return documents, metadatas, ids


def extract_topic_from_text(question_text: str, feedback: str = "") -> str:
    """
    Extract topic/theme from question text and feedback using keyword matching.

    This function analyzes the question text and feedback to determine the
    primary topic or theme using a predefined set of keywords for each topic.

    Args:
        question_text (str): The main question text to analyze.
        feedback (str, optional): Additional feedback text to include in analysis.
                                 Defaults to empty string.

    Returns:
        str: The extracted topic. Possible values include: 'accessibility',
             'navigation', 'forms', 'media', 'color', 'keyboard', 'content',
             or 'general' if no specific topic is detected.

    Note:
        The function uses a simple keyword-based approach to categorize
        questions into predefined topics related to web accessibility.
    """
    combined_text = f"{question_text} {feedback}".lower()

    # Simple keyword-based topic extraction
    topics = {
        "accessibility": [
            "accessibility",
            "screen reader",
            "alt text",
            "wcag",
            "disability",
            "inclusive",
        ],
        "navigation": ["navigation", "menu", "link", "breadcrumb", "sitemap"],
        "forms": ["form", "input", "label", "validation", "submit"],
        "media": ["image", "video", "audio", "media", "caption", "transcript"],
        "color": ["color", "contrast", "visual", "design", "appearance"],
        "keyboard": ["keyboard", "focus", "tab", "shortcut", "navigation"],
        "content": ["content", "text", "heading", "structure", "semantic"],
    }

    for topic, keywords in topics.items():
        if any(keyword in combined_text for keyword in keywords):
            return topic

    return "general"


def clean_answer_feedback(feedback: str, answer_text: str = "") -> str:
    """
    Clean AI-generated answer feedback by removing metadata and formatting artifacts.

    This function removes weight indicators, correctness markers, answer text
    references, and other metadata that may be included in AI-generated feedback
    to produce clean, user-friendly feedback text.

    Args:
        feedback (str): The raw AI-generated feedback text to clean.
        answer_text (str, optional): The answer text to remove if it appears
                                   at the beginning of the feedback. Defaults to empty string.

    Returns:
        str: The cleaned feedback text with metadata and formatting artifacts removed.

    Note:
        The function removes various patterns including:
        - Weight indicators like "(Weight: 100%)"
        - Correctness markers like "[✓ CORRECT]"
        - Answer text references at the beginning
        - Extra whitespace while preserving newlines
    """
    if not feedback:
        return feedback

    # Remove the answer text itself if it appears at the beginning
    if answer_text:
        # Escape special regex characters in the answer text
        escaped_answer_text = re.escape(answer_text.strip())
        # Remove answer text at the start, possibly followed by separators
        feedback = re.sub(
            rf"^\s*{escaped_answer_text}\s*[-–—:;.,]*\s*",
            "",
            feedback,
            flags=re.IGNORECASE,
        )

    # Remove patterns like "(Weight: 100%)", "(Weight: 0%)", etc.
    feedback = re.sub(r"\(Weight:\s*\d+%?\)", "", feedback, flags=re.IGNORECASE)

    # Remove correctness indicators like "[✓ CORRECT]", "[✗ INCORRECT]", etc.
    feedback = re.sub(
        r"\[.*?(?:CORRECT|INCORRECT).*?\]", "", feedback, flags=re.IGNORECASE
    )

    # Remove standalone correctness indicators
    feedback = re.sub(r"✓\s*CORRECT\s*[:-]?", "", feedback, flags=re.IGNORECASE)
    feedback = re.sub(r"✗\s*INCORRECT\s*[:-]?", "", feedback, flags=re.IGNORECASE)

    # Remove weight percentages at the start of lines
    feedback = re.sub(r"^\s*\d+%?\s*[:-]?\s*", "", feedback, flags=re.MULTILINE)

    # Clean up extra whitespace but preserve newlines
    # Replace multiple spaces with single space, but keep newlines
    feedback = re.sub(r"[ \t]+", " ", feedback)
    # Remove leading/trailing whitespace from each line
    feedback = "\n".join(line.strip() for line in feedback.split("\n"))
    # Remove empty lines at start and end
    feedback = feedback.strip()

    return feedback


def get_all_existing_tags(questions: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all unique tags from existing questions.

    This function parses the tags field from all questions and returns a
    sorted list of unique tags that can be used for suggestions or filtering.

    Args:
        questions (List[Dict[str, Any]]): List of question dictionaries to analyze.

    Returns:
        List[str]: Sorted list of unique tags found across all questions.

    Note:
        Tags are expected to be comma-separated strings in the 'tags' field
        of each question. The function handles whitespace and empty tags.
    """
    all_tags = set()

    for question in questions:
        tags = question.get("tags", "")
        if tags and isinstance(tags, str):
            # Split by comma and clean up whitespace
            question_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
            all_tags.update(question_tags)

    # Return sorted list of unique tags
    return sorted(list(all_tags))


async def search_vector_store(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the ChromaDB vector store for relevant chunks using semantic similarity.

    This function generates an embedding for the query text and searches the
    vector store for the most similar question chunks, returning them with
    their metadata and similarity scores.

    Args:
        query (str): The search query text.
        n_results (int, optional): Number of results to return. Defaults to 5.

    Returns:
        List[Dict[str, Any]]: List of chunk dictionaries, each containing:
            - 'content': The chunk text content
            - 'metadata': Associated metadata (question_id, topic, etc.)
            - 'distance': Similarity distance score (lower is more similar)

    Note:
        The function uses Ollama embeddings for the query and searches the
        ChromaDB collection named "quiz_questions". It handles errors gracefully
        and returns an empty list if the search fails.
    """
    try:
        client = chromadb.PersistentClient(path="./vector_store")
        collection = client.get_collection("quiz_questions")

        # Generate embedding for the query using Ollama
        query_embeddings = await get_ollama_embeddings([query])

        if not query_embeddings:
            logger.error("Failed to generate query embedding")
            return []

        # Search the vector store
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        chunks = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                chunk = {
                    "content": doc,
                    "metadata": results["metadatas"][0][i]
                    if results["metadatas"] and results["metadatas"][0]
                    else {},
                    "distance": results["distances"][0][i]
                    if results["distances"] and results["distances"][0]
                    else 0.0,
                }
                chunks.append(chunk)

        logger.info(f"Found {len(chunks)} relevant chunks for query: {query[:50]}...")
        return chunks

    except Exception as e:
        logger.error(f"Error searching vector store: {e}")
        return []


async def generate_feedback_with_ai(
    question_data: Dict[str, Any], system_prompt: str
) -> Dict[str, Any]:
    """
    Generate educational feedback for quiz questions using Azure OpenAI.

    This function sends a question to Azure OpenAI with a system prompt to
    generate comprehensive educational feedback including general feedback
    and answer-specific feedback for each answer option. It handles API
    communication, response parsing, and error conditions gracefully.

    Args:
        question_data (Dict[str, Any]): Question data including text, type,
                                      points, and answer options. Must contain
                                      'question_text' and 'answers' keys.
        system_prompt (str): The system prompt to guide the AI's response.
                            Should provide context about the educational role.

    Returns:
        Dict[str, Any]: Generated feedback containing:
            - 'general_feedback': Overall feedback for the question
            - 'answer_feedback': Dictionary mapping answer keys to feedback
            - 'token_usage': Token usage statistics from the API call

    Raises:
        HTTPException: If Azure OpenAI configuration is missing, API calls fail,
                      or the response is invalid.

    Note:
        The function validates Azure OpenAI configuration, constructs a detailed
        prompt with question context, and parses the AI response to extract
        structured feedback. It includes comprehensive error handling and logging.

    Example:
        >>> question_data = {
        ...     "id": 1,
        ...     "question_text": "What is the capital of France?",
        ...     "answers": [
        ...         {"id": 1, "text": "London", "weight": 0.0},
        ...         {"id": 2, "text": "Paris", "weight": 100.0}
        ...     ]
        ... }
        >>> system_prompt = "You are an educational assistant helping with quiz feedback."
        >>> feedback = await generate_feedback_with_ai(question_data, system_prompt)
        >>> print(feedback["general_feedback"])
        >>> print(feedback["answer_feedback"])

    See Also:
        :func:`get_ollama_embeddings`: Generate embeddings for vector search
        :func:`search_vector_store`: Search for similar questions
    """
    logger.info(
        f"Starting AI feedback generation for question ID: {question_data.get('id', 'unknown')}"
    )

    if not all(
        [
            AZURE_OPENAI_ENDPOINT,
            AZURE_OPENAI_DEPLOYMENT_ID,
            AZURE_OPENAI_SUBSCRIPTION_KEY,
        ]
    ):
        missing_configs = []
        if not AZURE_OPENAI_ENDPOINT:
            missing_configs.append("AZURE_OPENAI_ENDPOINT")
        if not AZURE_OPENAI_DEPLOYMENT_ID:
            missing_configs.append("AZURE_OPENAI_DEPLOYMENT_ID")
        if not AZURE_OPENAI_SUBSCRIPTION_KEY:
            missing_configs.append("AZURE_OPENAI_SUBSCRIPTION_KEY")
        logger.error(
            f"Missing Azure OpenAI configuration: {', '.join(missing_configs)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Azure OpenAI configuration incomplete. Missing: {', '.join(missing_configs)}",
        )

    # Construct the Azure OpenAI URL
    url = f"{AZURE_OPENAI_ENDPOINT}/us-east/deployments/{AZURE_OPENAI_DEPLOYMENT_ID}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    logger.info(f"Azure OpenAI URL: {url}")

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_OPENAI_SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }

    # Prepare question context for AI
    question_context = {
        "question_text": question_data.get("question_text", ""),
        "question_type": question_data.get("question_type", ""),
        "points_possible": question_data.get("points_possible", 0),
        "answers": [],
    }

    # Include answer information
    for answer in question_data.get("answers", []):
        question_context["answers"].append(
            {
                "text": answer.get("text", ""),
                "weight": answer.get("weight", 0),
                "is_correct": answer.get("weight", 0) > 0,
            }
        )

    # Create user message with question context
    user_message = f"""Please generate educational feedback for this web accessibility quiz question:

Question Type: {question_context['question_type']}
Question Text: {question_context['question_text']}
Points Possible: {question_context['points_possible']}

Answer Choices:
"""

    for i, answer in enumerate(question_context["answers"], 1):
        correct_indicator = "✓ CORRECT" if answer["is_correct"] else "✗ INCORRECT"
        user_message += f"{i}. {answer['text']} (Weight: {answer['weight']}%) [{correct_indicator}]\n"

    user_message += """
Format your response as:

Answer 1: [feedback for answer 1]
Answer 2: [feedback for answer 2]
Answer 3: [feedback for answer 3] (if applicable)
Answer 4: [feedback for answer 4] (if applicable)

Please provide specific educational feedback for each answer choice explaining why it is correct or incorrect.
"""

    #     user_message += """
    # Please provide comprehensive educational feedback following these guidelines:
    #
    # 1. GENERAL FEEDBACK:
    #    - Explain why this accessibility concept is important for creating inclusive web experiences
    #    - Describe how this relates to users with different types of disabilities
    #    - Reference relevant WCAG guidelines, success criteria, or accessibility standards
    #    - Connect to broader principles of inclusive design and user experience
    #    - Explain real-world implications and potential impact on users
    #
    # 2. ANSWER FEEDBACK:
    #    For each answer choice, provide detailed educational explanations:
    #
    #    **For CORRECT answers:**
    #    - Explain WHY this is the best practice for accessibility
    #    - Describe how it helps users with disabilities
    #    - Reference specific WCAG guidelines or standards it addresses
    #    - Provide implementation context and additional considerations
    #
    #    **For INCORRECT answers:**
    #    - Explain WHY this approach creates accessibility barriers
    #    - Describe which user groups would be most affected
    #    - Reference WCAG guidelines or standards it violates
    #    - Suggest what the correct approach should be instead
    #    - Explain potential legal or compliance implications
    #
    # Format your response as:
    #    Answer 1: [detailed educational feedback for first answer choice]
    #    Answer 2: [detailed educational feedback for second answer choice]
    #    [etc.]
    #
    # Focus on educational value - help students understand the principles behind web accessibility, not just the mechanics.
    # """

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 1500,
        "temperature": 0.7,
    }

    logger.info(
        f"Sending request to Azure OpenAI with payload keys: {list(payload.keys())}"
    )
    logger.debug(f"Full payload: {json.dumps(payload, indent=2)}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            logger.info(f"Azure OpenAI response status: {response.status_code}")

            if response.status_code != 200:
                response_text = response.text
                logger.error(f"Azure OpenAI API error response: {response_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI service error (status {response.status_code}): {response_text}",
                )

            result = response.json()
            logger.info(f"Azure OpenAI response received successfully")
            logger.debug(f"Full response: {json.dumps(result, indent=2)}")

            if "choices" not in result or not result["choices"]:
                logger.error("No choices in Azure OpenAI response")
                raise HTTPException(
                    status_code=500,
                    detail="Invalid response from AI service - no choices",
                )

            ai_response = result["choices"][0]["message"]["content"]
            logger.info(f"AI response content length: {len(ai_response)} characters")
            logger.debug(f"AI response content: {ai_response}")

            # Extract token usage information
            token_usage = {}
            if "usage" in result:
                token_usage = {
                    "prompt_tokens": result["usage"].get("prompt_tokens", 0),
                    "completion_tokens": result["usage"].get("completion_tokens", 0),
                    "total_tokens": result["usage"].get("total_tokens", 0),
                }
                logger.info(
                    f"Token usage - Prompt: {token_usage['prompt_tokens']}, "
                    f"Completion: {token_usage['completion_tokens']}, "
                    f"Total: {token_usage['total_tokens']}"
                )

            # Parse the AI response to extract general feedback and answer-specific feedback
            feedback = {
                "general_feedback": "",
                "answer_feedback": {},
                "token_usage": token_usage,
            }

            lines = ai_response.split("\n")
            current_section = None
            general_feedback_lines = []
            current_answer_key = None
            current_answer_text = []

            logger.info(f"Parsing AI response with {len(lines)} lines")

            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                logger.debug(f"Processing line {line_num}: {line}")

                # Look for section headers
                if any(
                    phrase in line.lower()
                    for phrase in [
                        "general feedback:",
                        "importance and relevance",
                        "1. general feedback",
                    ]
                ):
                    current_section = "general"
                    logger.info(f"Found general feedback section at line {line_num}")
                    # Extract content after colon if present
                    if ":" in line:
                        content = line.split(":", 1)[1].strip()
                        if content:
                            general_feedback_lines.append(content)
                elif any(
                    phrase in line.lower()
                    for phrase in [
                        "answer feedback:",
                        "2. answer feedback",
                        "answer 1:",
                    ]
                ):
                    current_section = "answers"
                    logger.info(f"Found answer feedback section at line {line_num}")
                    # Check if this line contains answer feedback
                    if "answer" in line.lower() and ":" in line:
                        if current_answer_key and current_answer_text:
                            # Extract answer number from key and get corresponding answer text
                            answer_text = ""
                            try:
                                match = re.search(r"\d+", current_answer_key)
                                if match:
                                    answer_number = (
                                        int(match.group()) - 1
                                    )  # Convert to 0-based index
                                    if (
                                        0
                                        <= answer_number
                                        < len(question_context["answers"])
                                    ):
                                        answer_text = question_context["answers"][
                                            answer_number
                                        ]["text"]
                            except (ValueError, IndexError):
                                pass

                            feedback["answer_feedback"][
                                current_answer_key
                            ] = clean_answer_feedback(
                                "\n".join(current_answer_text), answer_text
                            )

                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = (
                                [parts[1].strip()] if parts[1].strip() else []
                            )
                            logger.debug(f"Found answer key: {current_answer_key}")
                elif current_section == "general":
                    # Continue adding to general feedback
                    general_feedback_lines.append(line)
                elif current_section == "answers":
                    # Check if this is a new answer
                    if "answer" in line.lower() and ":" in line:
                        # Save previous answer if exists
                        if current_answer_key and current_answer_text:
                            # Extract answer number from key and get corresponding answer text
                            answer_text = ""
                            try:
                                match = re.search(r"\d+", current_answer_key)
                                if match:
                                    answer_number = (
                                        int(match.group()) - 1
                                    )  # Convert to 0-based index
                                    if (
                                        0
                                        <= answer_number
                                        < len(question_context["answers"])
                                    ):
                                        answer_text = question_context["answers"][
                                            answer_number
                                        ]["text"]
                            except (ValueError, IndexError):
                                pass

                            feedback["answer_feedback"][
                                current_answer_key
                            ] = clean_answer_feedback(
                                "\n".join(current_answer_text), answer_text
                            )

                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = (
                                [parts[1].strip()] if parts[1].strip() else []
                            )
                            logger.debug(f"Found answer key: {current_answer_key}")
                    elif current_answer_key:
                        # Continue adding to current answer feedback
                        current_answer_text.append(line)
                elif not current_section:
                    # Check if this line looks like an answer before defaulting to general feedback
                    if (
                        "answer" in line.lower()
                        and ":" in line
                        and re.search(r"answer\s*\d+\s*:", line, re.IGNORECASE)
                    ):
                        # This looks like "Answer 1:", "Answer 2:", etc. - switch to answers section
                        current_section = "answers"
                        logger.info(
                            f"Auto-detected answer section at line {line_num}: {line}"
                        )

                        # Process this line as an answer
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = (
                                [parts[1].strip()] if parts[1].strip() else []
                            )
                            logger.debug(f"Found answer key: {current_answer_key}")
                    else:
                        # Before any section is found, assume it's general feedback
                        general_feedback_lines.append(line)

            # Save the last answer if exists
            if current_answer_key and current_answer_text:
                # Extract answer number from key and get corresponding answer text
                answer_text = ""
                try:
                    # Extract number from keys like "answer 1", "answer1", "1", etc.
                    match = re.search(r"\d+", current_answer_key)
                    if match:
                        answer_number = (
                            int(match.group()) - 1
                        )  # Convert to 0-based index
                        if 0 <= answer_number < len(question_context["answers"]):
                            answer_text = question_context["answers"][answer_number][
                                "text"
                            ]
                except (ValueError, IndexError):
                    pass

                feedback["answer_feedback"][current_answer_key] = clean_answer_feedback(
                    "\n".join(current_answer_text), answer_text
                )

            # Combine general feedback lines
            feedback["general_feedback"] = "\n".join(general_feedback_lines)

            # If no structured parsing worked, put everything in general feedback
            if not feedback["general_feedback"] and not feedback["answer_feedback"]:
                logger.warning(
                    "Failed to parse AI response into sections, using full response as general feedback"
                )
                feedback["general_feedback"] = ai_response

            logger.info(
                f"Parsed feedback - General: {len(feedback['general_feedback'])} chars, "
                f"Answer feedback entries: {len(feedback['answer_feedback'])}"
            )

            return feedback

    except httpx.HTTPStatusError as e:
        logger.error(f"Azure OpenAI HTTP error: {e}")
        logger.error(
            f"Response text: {e.response.text if hasattr(e, 'response') else 'No response text'}"
        )
        raise HTTPException(
            status_code=e.response.status_code, detail=f"AI service HTTP error: {e}"
        )
    except httpx.TimeoutException as e:
        logger.error(f"Azure OpenAI timeout error: {e}")
        raise HTTPException(status_code=408, detail="AI service request timed out")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Azure OpenAI response as JSON: {e}")
        raise HTTPException(
            status_code=500, detail="Invalid JSON response from AI service"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating feedback: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate feedback: {str(e)}"
        )


async def fetch_courses() -> List[Dict[str, Any]]:
    """
    Fetch all available courses for the authenticated user from Canvas LMS.

    This function retrieves a list of courses that the user has access to,
    including course metadata such as name, code, and term information.

    Returns:
        List[Dict[str, Any]]: List of course dictionaries containing:
            - 'id': Canvas course ID
            - 'name': Course name
            - 'course_code': Course code/short name
            - 'enrollment_term_id': Term ID
            - 'term': Term name

    Raises:
        HTTPException: If Canvas configuration is missing or API calls fail.

    Note:
        The function filters for active enrollments and includes term information.
        It requires valid Canvas API configuration (base URL and token).
    """
    if not all([CANVAS_BASE_URL, CANVAS_API_TOKEN]):
        logger.error("Missing Canvas configuration")
        raise HTTPException(
            status_code=400, detail="Canvas API configuration is incomplete"
        )

    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    courses = []

    try:
        url = f"{CANVAS_BASE_URL}/api/v1/courses"
        params = {"enrollment_state": "active", "per_page": 100, "include": ["term"]}

        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching courses from: {url}")
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            courses_data = response.json()

            for course in courses_data:
                courses.append(
                    {
                        "id": course.get("id"),
                        "name": course.get("name"),
                        "course_code": course.get("course_code"),
                        "enrollment_term_id": course.get("enrollment_term_id"),
                        "term": course.get("term", {}).get("name", "Unknown Term")
                        if course.get("term")
                        else "Unknown Term",
                    }
                )

            logger.info(f"Fetched {len(courses)} courses")
            return courses

    except httpx.HTTPStatusError as e:
        logger.error(f"Canvas API HTTP error fetching courses: {e}")
        raise HTTPException(
            status_code=e.response.status_code, detail=f"Canvas API error: {e}"
        )
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch courses: {str(e)}"
        )


async def fetch_quizzes(course_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all quizzes for a specific course from Canvas LMS.

    This function retrieves a list of quizzes available in the specified course,
    including quiz metadata such as title, description, and question count.

    Args:
        course_id (str): The Canvas course ID to fetch quizzes for.

    Returns:
        List[Dict[str, Any]]: List of quiz dictionaries containing:
            - 'id': Canvas quiz ID
            - 'title': Quiz title
            - 'description': Quiz description
            - 'question_count': Number of questions in the quiz
            - 'published': Whether the quiz is published
            - 'due_at': Quiz due date
            - 'quiz_type': Type of quiz

    Raises:
        HTTPException: If Canvas configuration is missing or API calls fail.

    Note:
        The function requires valid Canvas API configuration and the user
        must have access to the specified course.
    """
    if not all([CANVAS_BASE_URL, CANVAS_API_TOKEN]):
        logger.error("Missing Canvas configuration")
        raise HTTPException(
            status_code=400, detail="Canvas API configuration is incomplete"
        )

    headers = {"Authorization": f"Bearer {CANVAS_API_TOKEN}"}
    quizzes = []

    try:
        url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/quizzes"
        params = {"per_page": 100}

        async with httpx.AsyncClient() as client:
            logger.info(f"Fetching quizzes for course {course_id} from: {url}")
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            quizzes_data = response.json()

            for quiz in quizzes_data:
                quizzes.append(
                    {
                        "id": quiz.get("id"),
                        "title": quiz.get("title"),
                        "description": quiz.get("description", ""),
                        "question_count": quiz.get("question_count", 0),
                        "published": quiz.get("published", False),
                        "due_at": quiz.get("due_at"),
                        "quiz_type": quiz.get("quiz_type", "assignment"),
                    }
                )

            logger.info(f"Fetched {len(quizzes)} quizzes for course {course_id}")
            return quizzes

    except httpx.HTTPStatusError as e:
        logger.error(f"Canvas API HTTP error fetching quizzes: {e}")
        raise HTTPException(
            status_code=e.response.status_code, detail=f"Canvas API error: {e}"
        )
    except Exception as e:
        logger.error(f"Error fetching quizzes for course {course_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch quizzes: {str(e)}"
        )


async def fetch_all_questions() -> List[Dict[str, Any]]:
    """
    Fetch all questions from a Canvas quiz with pagination support.

    This function retrieves all questions from the configured Canvas quiz,
    handling pagination automatically and cleaning question text by removing
    unwanted HTML tags.

    Returns:
        List[Dict[str, Any]]: List of question dictionaries from the Canvas quiz.

    Raises:
        HTTPException: If Canvas configuration is missing or API calls fail.

    Note:
        The function uses the globally configured COURSE_ID and QUIZ_ID.
        It automatically handles pagination and cleans question text to remove
        unwanted HTML tags like link, script, and style tags.
    """
    if not all([CANVAS_BASE_URL, CANVAS_API_TOKEN, COURSE_ID, QUIZ_ID]):
        raise HTTPException(status_code=500, detail="Missing Canvas configuration")

    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}",
        "Content-Type": "application/json",
    }

    all_questions = []
    page = 1
    per_page = 100

    while True:
        url = (
            f"{CANVAS_BASE_URL}/api/v1/courses/{COURSE_ID}/quizzes/{QUIZ_ID}/questions"
        )
        params = f"?page={page}&per_page={per_page}"

        logger.info(f"Fetching page {page} from Canvas API")
        data = await make_canvas_request(url + params, headers)

        if not data:
            break

        # Clean question text from unwanted HTML tags
        for question in data:
            if "question_text" in question and question["question_text"]:
                question["question_text"] = clean_question_text(
                    question["question_text"]
                )

        all_questions.extend(data)

        # Check if we got fewer results than requested (last page)
        if len(data) < per_page:
            break

        page += 1

    logger.info(f"Fetched {len(all_questions)} questions from Canvas")
    return all_questions


# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Home page endpoint displaying all quiz questions.

    This endpoint serves the main application page that displays all questions
    in a table format with options to edit, delete, and generate AI feedback.

    Args:
        request (Request): FastAPI request object.

    Returns:
        HTMLResponse: Rendered index.html template with questions data.

    Raises:
        HTTPException: If there's an error loading questions or rendering the template.

    Note:
        The response includes cache-busting headers to prevent browser caching issues.
        The template receives questions data, course ID, and quiz ID for display.
    """
    try:
        questions = load_questions()

        # Create response with cache-busting headers
        response = templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "questions": questions,
                "course_id": COURSE_ID,
                "quiz_id": QUIZ_ID,
            },
        )

        # Add cache-busting headers to prevent browser caching issues
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response
    except Exception as e:
        logger.error(f"Error loading home page: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to load questions: {str(e)}"
        )


@app.get("/api/courses")
async def get_courses():
    """Get all available courses"""
    try:
        courses = await fetch_courses()
        return {"success": True, "courses": courses}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses/{course_id}/quizzes")
async def get_quizzes(course_id: str):
    """Get all quizzes for a specific course"""
    try:
        quizzes = await fetch_quizzes(course_id)
        return {"success": True, "quizzes": quizzes}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quizzes for course {course_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/configuration")
async def update_configuration(config_data: dict):
    """Update course and quiz configuration"""
    try:
        global COURSE_ID, QUIZ_ID

        course_id = config_data.get("course_id")
        quiz_id = config_data.get("quiz_id")

        if course_id:
            COURSE_ID = str(course_id)
        if quiz_id:
            QUIZ_ID = str(quiz_id)

        logger.info(
            f"Updated configuration: Course ID = {COURSE_ID}, Quiz ID = {QUIZ_ID}"
        )
        return {"success": True, "message": "Configuration updated successfully"}

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fetch-questions")
async def fetch_questions():
    """Fetch questions from Canvas API"""
    try:
        questions = await fetch_all_questions()
        if save_questions(questions):
            logger.info(f"Successfully saved {len(questions)} questions")
            return {
                "success": True,
                "message": f"Fetched and saved {len(questions)} questions",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save questions")
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/questions/{question_id}")
async def delete_question(question_id: int):
    """Delete a question from the dataset"""
    try:
        questions = load_questions()
        questions = [q for q in questions if q.get("id") != question_id]

        if save_questions(questions):
            logger.info(f"Deleted question {question_id}")
            return {"success": True, "message": "Question deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save changes")
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/questions/new", response_class=HTMLResponse)
async def new_question_page(request: Request):
    """Show new question creation page"""
    questions = load_questions()

    # Create a template new question
    new_question = {
        "id": "new",
        "question_text": "Enter your question text here...",
        "question_type": "multiple_choice_question",
        "points_possible": 1.0,
        "quiz_id": QUIZ_ID,
        "topic": "general",
        "tags": "",
        "learning_objective": "",
        "neutral_comments": "",
        "answers": [
            {"id": 1, "text": "Answer option 1", "weight": 100, "html": ""},
            {"id": 2, "text": "Answer option 2", "weight": 0, "html": ""},
            {"id": 3, "text": "Answer option 3", "weight": 0, "html": ""},
            {"id": 4, "text": "Answer option 4", "weight": 0, "html": ""},
        ],
    }

    # Available topic options
    available_topics = [
        ("accessibility", "Accessibility"),
        ("navigation", "Navigation"),
        ("forms", "Forms"),
        ("media", "Media"),
        ("color", "Color & Contrast"),
        ("keyboard", "Keyboard"),
        ("content", "Content & Structure"),
        ("general", "General"),
    ]

    # Get all existing tags for suggestions
    existing_tags = get_all_existing_tags(questions)

    # Get learning objectives for dropdown
    learning_objectives = load_objectives()

    return templates.TemplateResponse(
        "edit_question.html",
        {
            "request": request,
            "question": new_question,
            "available_topics": available_topics,
            "existing_tags": existing_tags,
            "learning_objectives": learning_objectives,
            "prev_question_id": None,
            "next_question_id": None,
            "current_position": 0,
            "total_questions": len(questions),
            "is_new_question": True,
        },
    )


@app.post("/questions/new")
async def create_new_question(question_data: QuestionUpdate):
    """Create a new question"""
    try:
        questions = load_questions()

        # Generate new ID (find the highest existing ID and add 1)
        max_id = max([q.get("id", 0) for q in questions] + [0])
        new_id = max_id + 1

        # Create new question object
        new_question = {
            "id": new_id,
            "question_text": question_data.question_text,
            "question_type": "multiple_choice_question",  # Default type
            "points_possible": 1.0,  # Default points
            "quiz_id": QUIZ_ID,
            "topic": question_data.topic,
            "tags": question_data.tags,
            "learning_objective": question_data.learning_objective,
            "correct_comments": question_data.correct_comments,
            "incorrect_comments": question_data.incorrect_comments,
            "neutral_comments": question_data.neutral_comments,
            "correct_comments_html": question_data.correct_comments_html,
            "incorrect_comments_html": question_data.incorrect_comments_html,
            "neutral_comments_html": question_data.neutral_comments_html,
            "answers": [answer.model_dump() for answer in question_data.answers],
        }

        # Add to questions list
        questions.append(new_question)

        if save_questions(questions):
            logger.info(f"Created new question with ID {new_id}")
            return {
                "success": True,
                "message": "Question created successfully",
                "question_id": new_id,
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save new question")
    except Exception as e:
        logger.error(f"Error creating new question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/questions/{question_id}", response_class=HTMLResponse)
async def edit_question(request: Request, question_id: int):
    """Show question edit page"""
    questions = load_questions()
    question = next((q for q in questions if q.get("id") == question_id), None)

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Find previous and next question IDs for navigation
    question_ids = [q.get("id") for q in questions]
    current_index = question_ids.index(question_id)

    prev_question_id = question_ids[current_index - 1] if current_index > 0 else None
    next_question_id = (
        question_ids[current_index + 1]
        if current_index < len(question_ids) - 1
        else None
    )

    # Ensure question has a topic field (backward compatibility)
    if "topic" not in question:
        question["topic"] = extract_topic_from_text(
            question.get("question_text", ""), question.get("neutral_comments", "")
        )

    # Ensure question has a tags field (backward compatibility)
    if "tags" not in question:
        question["tags"] = ""

    # Ensure question has a learning_objective field (backward compatibility)
    if "learning_objective" not in question:
        question["learning_objective"] = ""

    # Available topic options
    available_topics = [
        ("accessibility", "Accessibility"),
        ("navigation", "Navigation"),
        ("forms", "Forms"),
        ("media", "Media"),
        ("color", "Color & Contrast"),
        ("keyboard", "Keyboard"),
        ("content", "Content & Structure"),
        ("general", "General"),
    ]

    # Get all existing tags for suggestions
    existing_tags = get_all_existing_tags(questions)

    # Get learning objectives for dropdown
    learning_objectives = load_objectives()

    return templates.TemplateResponse(
        "edit_question.html",
        {
            "request": request,
            "question": question,
            "available_topics": available_topics,
            "existing_tags": existing_tags,
            "learning_objectives": learning_objectives,
            "prev_question_id": prev_question_id,
            "next_question_id": next_question_id,
            "current_position": current_index + 1,
            "total_questions": len(questions),
        },
    )


@app.get("/system-prompt", response_class=HTMLResponse)
async def get_system_prompt_page(request: Request):
    """Get the system prompt editing page"""
    prompt = load_system_prompt()
    return templates.TemplateResponse(
        "system_prompt_edit.html", {"request": request, "current_prompt": prompt}
    )


@app.get("/system-prompt/api")
async def get_system_prompt_api():
    """Get the current system prompt as JSON (for API calls)"""
    prompt = load_system_prompt()
    return {"prompt": prompt}


@app.post("/system-prompt")
async def save_system_prompt_endpoint(prompt: str = Form(...)):
    """Save the system prompt"""
    try:
        if save_system_prompt(prompt):
            logger.info("System prompt updated")
            return {"success": True, "message": "System prompt saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save system prompt")
    except Exception as e:
        logger.error(f"Error saving system prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/questions/{question_id}/generate-feedback")
async def generate_question_feedback(question_id: int):
    """Generate AI feedback for a question"""
    logger.info(f"=== Generate Feedback Request Started for Question {question_id} ===")

    try:
        # Load system prompt
        logger.info("Loading system prompt...")
        system_prompt = load_system_prompt()
        if not system_prompt:
            logger.error("No system prompt found")
            raise HTTPException(
                status_code=400,
                detail="No system prompt configured. Please set a system prompt first.",
            )

        logger.info(
            f"System prompt loaded successfully (length: {len(system_prompt)} characters)"
        )

        # Find the question
        logger.info(f"Loading questions to find question {question_id}...")
        questions = load_questions()
        logger.info(f"Loaded {len(questions)} questions from file")

        question = next((q for q in questions if q.get("id") == question_id), None)

        if not question:
            logger.error(f"Question {question_id} not found in dataset")
            raise HTTPException(status_code=404, detail="Question not found")

        logger.info(
            f"Found question: type={question.get('question_type')}, text_length={len(question.get('question_text', ''))}"
        )
        logger.info(f"Question has {len(question.get('answers', []))} answers")

        # Generate feedback using AI
        logger.info("Starting AI feedback generation...")
        feedback = await generate_feedback_with_ai(question, system_prompt)
        logger.info("AI feedback generation completed successfully")

        # Update the question with generated feedback
        logger.info("Updating question with generated feedback...")
        question_index = next(
            (i for i, q in enumerate(questions) if q.get("id") == question_id), None
        )
        if question_index is not None:
            logger.info(f"Found question at index {question_index}")

            # Update the general feedback
            questions[question_index]["neutral_comments"] = feedback["general_feedback"]

            # Update answer-specific feedback
            for i, answer in enumerate(questions[question_index].get("answers", [])):
                # Try different keys to match the answer
                answer_keys_to_try = [
                    f"answer {i+1}",
                    f"answer{i+1}",
                    f"{i+1}",
                    str(i + 1),
                ]

                for key in answer_keys_to_try:
                    if key in feedback["answer_feedback"]:
                        answer["comments"] = feedback["answer_feedback"][key]
                        logger.info(f"Updated answer {i+1} feedback")
                        break

            logger.info("Saving updated questions to file...")
            if save_questions(questions):
                logger.info(
                    f"Successfully generated and saved AI feedback for question {question_id}"
                )
                return {
                    "success": True,
                    "message": "Feedback generated successfully",
                    "feedback": feedback,
                }
            else:
                logger.error("Failed to save questions to file")
                raise HTTPException(
                    status_code=500, detail="Failed to save generated feedback"
                )
        else:
            logger.error(f"Could not find question {question_id} for update")
            raise HTTPException(status_code=404, detail="Question not found for update")

    except HTTPException as e:
        # Re-raise HTTP exceptions (they're already properly formatted)
        logger.error(f"HTTP Exception in generate_question_feedback: {e.detail}")
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error generating feedback for question {question_id}: {e}"
        )
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error args: {e.args}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/debug/question/{question_id}")
async def debug_question(question_id: int):
    """Debug endpoint to inspect a specific question"""
    try:
        questions = load_questions()
        question = next((q for q in questions if q.get("id") == question_id), None)

        if not question:
            return {"question_found": False, "total_questions": len(questions)}

        return {
            "question_found": True,
            "question_id": question.get("id"),
            "question_type": question.get("question_type"),
            "question_text_length": len(question.get("question_text", "")),
            "answers_count": len(question.get("answers", [])),
            "has_correct_comments": bool(question.get("correct_comments")),
            "has_incorrect_comments": bool(question.get("incorrect_comments")),
            "has_neutral_comments": bool(question.get("neutral_comments")),
            "question_keys": list(question.keys()),
            "total_questions": len(questions),
        }
    except Exception as e:
        return {
            "question_found": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


@app.post("/create-vector-store")
async def create_vector_store():
    """Create ChromaDB vector store from quiz questions using Azure embeddings"""
    logger.info("=== Vector Store Creation Started ===")

    try:
        # Load questions
        logger.info("Loading questions from JSON file...")
        questions = load_questions()
        if not questions:
            raise HTTPException(
                status_code=400, detail="No questions found to create vector store"
            )

        logger.info(f"Loaded {len(questions)} questions for vector store creation")

        # Create comprehensive chunks
        logger.info("Creating comprehensive chunks from questions...")
        documents, metadatas, ids = create_comprehensive_chunks(questions)
        logger.info(f"Created {len(documents)} document chunks")

        # Generate embeddings using Ollama nomic-embed-text
        logger.info("Generating embeddings using Ollama nomic-embed-text model...")
        embeddings = await get_ollama_embeddings(documents)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Initialize ChromaDB
        logger.info("Initializing ChromaDB client...")
        client = chromadb.PersistentClient(path="./vector_store")

        # Delete existing collection if it exists
        try:
            client.delete_collection("quiz_questions")
            logger.info("Deleted existing vector store collection")
        except Exception:
            logger.info("No existing collection to delete")

        # Create new collection
        collection = client.create_collection(
            name="quiz_questions",
            metadata={"description": "Quiz questions with comprehensive content"},
        )

        # Add documents to collection
        logger.info("Adding documents to ChromaDB collection...")
        collection.add(
            documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids
        )

        # Create summary statistics
        topic_counts = {}
        question_type_counts = {}
        tag_counts = {}

        for metadata in metadatas:
            topic = metadata.get("topic", "unknown")
            question_type = metadata.get("question_type", "unknown")
            tags = metadata.get("tags", "")

            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            question_type_counts[question_type] = (
                question_type_counts.get(question_type, 0) + 1
            )

            # Count individual tags
            if tags:
                individual_tags = [
                    tag.strip() for tag in tags.split(",") if tag.strip()
                ]
                for tag in individual_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        logger.info("Vector store creation completed successfully")

        return {
            "success": True,
            "message": f"Successfully created vector store with {len(documents)} questions",
            "stats": {
                "total_questions": len(documents),
                "total_embeddings": len(embeddings),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "topics": topic_counts,
                "question_types": question_type_counts,
                "tags": tag_counts,
                "vector_store_path": "./vector_store",
            },
        }

    except HTTPException as e:
        logger.error(f"HTTP Exception in create_vector_store: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating vector store: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create vector store: {str(e)}"
        )


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat assistant page"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.post("/chat/message")
async def chat_message(request: Request):
    """Process chat message with RAG using vector store"""
    try:
        # Parse request body
        body = await request.json()
        user_message = body.get("message", "").strip()
        max_chunks = body.get("max_chunks", 3)

        # Validate max_chunks
        if not isinstance(max_chunks, int) or max_chunks < 1 or max_chunks > 10:
            max_chunks = 3

        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        logger.info(f"=== Chat Message Processing Started ===")
        logger.info(f"User message: {user_message}")
        logger.info(f"Max chunks requested: {max_chunks}")

        # Search vector store for relevant chunks
        logger.info("Searching vector store for relevant context...")
        retrieved_chunks = await search_vector_store(user_message, n_results=max_chunks)
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks")

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(f"Context {i+1}:\n{chunk['content']}")

        context = (
            "\n\n".join(context_parts)
            if context_parts
            else "No relevant context found."
        )

        # Load custom chat system prompt and inject context
        chat_system_prompt_template = load_chat_system_prompt()
        system_prompt = chat_system_prompt_template.format(context=context)

        # Prepare messages for Azure OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Call Azure OpenAI for chat completion
        logger.info("Calling Azure OpenAI for chat completion...")

        url = f"{AZURE_OPENAI_ENDPOINT}/us-east/deployments/{AZURE_OPENAI_DEPLOYMENT_ID}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"

        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_OPENAI_SUBSCRIPTION_KEY,
            "Content-Type": "application/json",
        }

        payload = {
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Azure OpenAI API error: {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI service error: {error_text}",
                )

            result = response.json()

            if "choices" not in result or not result["choices"]:
                raise HTTPException(
                    status_code=500, detail="Invalid response from AI service"
                )

            ai_response = result["choices"][0]["message"]["content"]

            # Log token usage if available
            if "usage" in result:
                usage = result["usage"]
                logger.info(
                    f"Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                    f"Completion: {usage.get('completion_tokens', 0)}, "
                    f"Total: {usage.get('total_tokens', 0)}"
                )

        logger.info("Chat message processed successfully")

        return {
            "response": ai_response,
            "retrieved_chunks": retrieved_chunks,
            "context_used": len(context_parts) > 0,
        }

    except HTTPException as e:
        logger.error(f"HTTP Exception in chat_message: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in chat_message: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process chat message: {str(e)}"
        )


@app.get("/chat-system-prompt", response_class=HTMLResponse)
async def chat_system_prompt_page(request: Request):
    """Chat system prompt edit page"""
    current_prompt = load_chat_system_prompt()
    default_prompt = get_default_chat_system_prompt()

    return templates.TemplateResponse(
        "chat_system_prompt_edit.html",
        {
            "request": request,
            "current_prompt": current_prompt,
            "default_prompt": default_prompt,
        },
    )


@app.post("/chat-system-prompt")
async def save_chat_system_prompt_endpoint(request: Request):
    """Save chat system prompt"""
    try:
        form = await request.form()
        prompt = form.get("prompt", "").strip()

        if not prompt:
            raise HTTPException(status_code=400, detail="System prompt cannot be empty")

        if save_chat_system_prompt(prompt):
            logger.info("Chat system prompt saved successfully")
            return {"success": True, "message": "Chat system prompt saved successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save chat system prompt"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error saving chat system prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat-system-prompt/default")
async def get_default_chat_system_prompt_endpoint():
    """Get default chat system prompt"""
    return {"default_prompt": get_default_chat_system_prompt()}


@app.get("/chat-welcome-message")
async def get_chat_welcome_message():
    """Get the current chat welcome message"""
    try:
        welcome_message = load_welcome_message()
        return {"welcome_message": welcome_message}
    except Exception as e:
        logger.error(f"Error loading welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat-welcome-message")
async def save_chat_welcome_message(request: Request):
    """Save chat welcome message"""
    try:
        # Check if it's JSON or form data
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            body = await request.json()
            message = body.get("welcome_message", "").strip()
        else:
            form = await request.form()
            message = form.get("welcome_message", "").strip()

        if not message:
            raise HTTPException(
                status_code=400, detail="Welcome message cannot be empty"
            )

        if save_welcome_message(message):
            logger.info("Welcome message saved successfully")
            return {"success": True, "message": "Welcome message saved successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save welcome message"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error saving welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat-welcome-message/default")
async def get_default_chat_welcome_message():
    """Get default chat welcome message"""
    try:
        default_message = get_default_welcome_message()
        return {"default_welcome_message": default_message}
    except Exception as e:
        logger.error(f"Error loading default welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test-system-prompt", response_class=HTMLResponse)
async def test_system_prompt_page(request: Request):
    """Test page for system prompt functionality"""
    return templates.TemplateResponse("test_system_prompt.html", {"request": request})


@app.get("/objectives", response_class=HTMLResponse)
async def objectives_page(request: Request):
    """Learning objectives management page"""
    objectives = load_objectives()
    return templates.TemplateResponse(
        "objectives.html", {"request": request, "objectives": objectives}
    )


@app.post("/objectives")
async def save_objectives_endpoint(objectives_data: ObjectivesUpdate):
    """Save learning objectives"""
    try:
        # Convert Pydantic models to dictionaries
        objectives_list = [obj.model_dump() for obj in objectives_data.objectives]

        if save_objectives(objectives_list):
            logger.info(f"Saved {len(objectives_list)} learning objectives")
            return {
                "success": True,
                "message": f"Successfully saved {len(objectives_list)} learning objectives",
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save learning objectives"
            )
    except Exception as e:
        logger.error(f"Error saving objectives: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration"""
    return {
        "canvas_configured": bool(
            CANVAS_BASE_URL and CANVAS_API_TOKEN and COURSE_ID and QUIZ_ID
        ),
        "azure_configured": bool(
            AZURE_OPENAI_ENDPOINT
            and AZURE_OPENAI_DEPLOYMENT_ID
            and AZURE_OPENAI_SUBSCRIPTION_KEY
        ),
        "has_system_prompt": bool(load_system_prompt()),
        "data_file_exists": os.path.exists(DATA_FILE),
        "questions_count": len(load_questions()) if os.path.exists(DATA_FILE) else 0,
        "azure_endpoint": AZURE_OPENAI_ENDPOINT,
        "azure_deployment_id": AZURE_OPENAI_DEPLOYMENT_ID,
        "azure_api_version": AZURE_OPENAI_API_VERSION,
        "ollama_host": OLLAMA_HOST,
        "ollama_embedding_model": OLLAMA_EMBEDDING_MODEL,
        "ollama_host_with_protocol": OLLAMA_HOST
        if OLLAMA_HOST.startswith(("http://", "https://"))
        else f"http://{OLLAMA_HOST}",
    }


@app.get("/debug/ollama-test")
async def test_ollama_connection():
    """Test Ollama connection and model availability"""
    ollama_host = OLLAMA_HOST
    if not ollama_host.startswith(("http://", "https://")):
        ollama_host = f"http://{ollama_host}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test basic connection
            response = await client.get(f"{ollama_host}/api/tags")

            if response.status_code == 200:
                models = response.json()
                model_names = [model["name"] for model in models.get("models", [])]

                return {
                    "ollama_connected": True,
                    "ollama_host": ollama_host,
                    "available_models": model_names,
                    "embedding_model_available": OLLAMA_EMBEDDING_MODEL in model_names,
                    "configured_model": OLLAMA_EMBEDDING_MODEL,
                }
            else:
                return {
                    "ollama_connected": False,
                    "error": f"Ollama returned status {response.status_code}",
                    "ollama_host": ollama_host,
                }

    except httpx.ConnectError as e:
        return {
            "ollama_connected": False,
            "error": f"Cannot connect to Ollama at {ollama_host}",
            "ollama_host": ollama_host,
            "details": str(e),
        }
    except Exception as e:
        return {
            "ollama_connected": False,
            "error": f"Unexpected error: {str(e)}",
            "ollama_host": ollama_host,
        }


@app.put("/questions/{question_id}")
async def update_question(question_id: int, question_data: QuestionUpdate):
    """Update a question"""
    try:
        questions = load_questions()
        question_index = next(
            (i for i, q in enumerate(questions) if q.get("id") == question_id), None
        )

        if question_index is None:
            raise HTTPException(status_code=404, detail="Question not found")

        # Update the question
        questions[question_index].update(
            {
                "question_text": question_data.question_text,
                "topic": question_data.topic,
                "tags": question_data.tags,
                "learning_objective": question_data.learning_objective,
                "correct_comments": question_data.correct_comments,
                "incorrect_comments": question_data.incorrect_comments,
                "neutral_comments": question_data.neutral_comments,
                "correct_comments_html": question_data.correct_comments_html,
                "incorrect_comments_html": question_data.incorrect_comments_html,
                "neutral_comments_html": question_data.neutral_comments_html,
                "answers": [answer.model_dump() for answer in question_data.answers],
            }
        )

        if save_questions(questions):
            logger.info(f"Updated question {question_id}")
            return {"success": True, "message": "Question updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save changes")
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without wrapping them
        raise
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def start():
    """
    Entry point for production server startup.

    This function starts the FastAPI application in production mode using uvicorn.
    The server runs on all interfaces (0.0.0.0) on port 8080.

    Note:
        This function is designed to be called from the command line or
        as a Poetry script entry point for production deployment.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)


def dev():
    """
    Entry point for development server startup with auto-reload.

    This function starts the FastAPI application in development mode using uvicorn
    with auto-reload enabled. The server runs on all interfaces (0.0.0.0) on port 8080.

    Note:
        This function is designed to be called from the command line or
        as a Poetry script entry point for development with hot reloading.
    """
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
