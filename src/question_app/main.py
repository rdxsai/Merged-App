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

# Import API routers
from .api import canvas_router, questions_router

# Import utility functions from organized modules
from .utils import (
    load_questions,
    save_questions,
    load_objectives,
    save_objectives,
    load_system_prompt,
    save_system_prompt,
    load_chat_system_prompt,
    save_chat_system_prompt,
    load_welcome_message,
    save_welcome_message,
    get_default_chat_system_prompt,
    get_default_welcome_message,
    clean_question_text,
    clean_html_for_vector_store,
    clean_answer_feedback,
    get_all_existing_tags,
    extract_topic_from_text,
)

app = FastAPI(title="Canvas Quiz Manager")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(canvas_router)
app.include_router(questions_router)

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
DATA_FILE = "data/quiz_questions.json"
SYSTEM_PROMPT_FILE = "config/system_prompt.txt"
CHAT_SYSTEM_PROMPT_FILE = "config/chat_system_prompt.txt"
WELCOME_MESSAGE_FILE = "config/chat_welcome_message.txt"


# Import models from the models package
from .models import (
    Answer,
    Question,
    QuestionUpdate,
    NewQuestion,
    LearningObjective,
    ObjectivesUpdate,
)



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
        objectives_file = "data/learning_objectives.json"
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
        objectives_file = "data/learning_objectives.json"
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

    uvicorn.run("question_app.main:app", host="0.0.0.0", port=8080, reload=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
