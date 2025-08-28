"""
Debug API module for the Question App.

This module contains all debugging and testing functionality including:
- Question debugging endpoints
- Configuration debugging endpoints
- Ollama connection testing endpoints
"""

import os
from typing import Dict, Any  # noqa: F401

import httpx
from fastapi import APIRouter

from ..core import config, get_logger
from ..utils import load_questions, load_system_prompt

logger = get_logger(__name__)

# Create router for debug endpoints
router = APIRouter(prefix="/debug", tags=["debug"])

# File paths
DATA_FILE = "data/quiz_questions.json"
SYSTEM_PROMPT_FILE = "config/system_prompt.txt"


@router.get("/question/{question_id}")
async def debug_question(question_id: int):
    """
    Debug endpoint to inspect a specific question.
    
    This endpoint provides detailed information about a specific question
    including its structure, content length, and metadata.
    
    Args:
        question_id (int): The ID of the question to debug.
        
    Returns:
        Dict[str, Any]: Debug information about the question including:
            - question_found: Whether the question exists
            - question_id: The question ID
            - question_type: Type of question
            - question_text_length: Length of question text
            - answers_count: Number of answer options
            - has_correct_comments: Whether correct comments exist
            - has_incorrect_comments: Whether incorrect comments exist
            - has_neutral_comments: Whether neutral comments exist
            - question_keys: All keys present in the question object
            - total_questions: Total number of questions in the dataset
    """
    try:
        questions = load_questions()
        question = next((q for q in questions if q.get("id") == question_id), None)

        if not question:
            return {"question_found": False, "total_questions": len(questions)}

        return {
            "question_found": True,
            "question_id": question.get("id"),
            "question_type": question.get("question_type"),
            "question_text_length": len(
                question.get("question_text", "")
            ),
            "answers_count": len(question.get("answers", [])),
            "has_correct_comments": bool(
                question.get("correct_comments")
            ),
            "has_incorrect_comments": bool(
                question.get("incorrect_comments")
            ),
            "has_neutral_comments": bool(
                question.get("neutral_comments")
            ),
            "question_keys": list(question.keys()),
            "total_questions": len(questions),
        }
    except Exception as e:
        return {
            "question_found": False,
            "error": str(e),
            "error_type": type(e).__name__,
        }


@router.get("/config")
async def debug_config():
    """
    Debug endpoint to check configuration.
    
    This endpoint provides information about the application's configuration
    including Canvas LMS settings, Azure OpenAI settings, and system status.
    
    Returns:
        Dict[str, Any]: Configuration debug information including:
            - canvas_configured: Whether Canvas is properly configured
            - azure_configured: Whether Azure OpenAI is properly configured
            - has_system_prompt: Whether system prompt file exists
            - data_file_exists: Whether questions data file exists
            - questions_count: Number of questions loaded
            - azure_endpoint: Azure OpenAI endpoint URL
            - azure_deployment_id: Azure OpenAI deployment ID
            - azure_api_version: Azure OpenAI API version
            - ollama_host: Ollama host configuration
            - ollama_embedding_model: Ollama embedding model
            - ollama_host_with_protocol: Full Ollama URL with protocol
    """
    # Configuration is now handled by the core config module
    
    return {
        "canvas_configured": config.validate_canvas_config(),
        "azure_configured": config.validate_azure_openai_config(),
        "has_system_prompt": bool(load_system_prompt()),
        "data_file_exists": os.path.exists(DATA_FILE),
        "questions_count": len(load_questions()) if os.path.exists(DATA_FILE) else 0,
        "azure_endpoint": config.AZURE_OPENAI_ENDPOINT,
        "azure_deployment_id": config.AZURE_OPENAI_DEPLOYMENT_ID,
        "azure_api_version": config.AZURE_OPENAI_API_VERSION,
        "ollama_host": config.OLLAMA_HOST,
        "ollama_embedding_model": config.OLLAMA_EMBEDDING_MODEL,
        "ollama_host_with_protocol": config.OLLAMA_HOST
        if config.OLLAMA_HOST.startswith(("http://", "https://"))
        else f"http://{config.OLLAMA_HOST}",
    }


@router.get("/ollama-test")
async def test_ollama_connection():
    """
    Test Ollama connection and model availability.
    
    This endpoint tests the connection to the Ollama service and checks
    if the configured embedding model is available.
    
    Returns:
        Dict[str, Any]: Ollama connection test results including:
            - ollama_connected: Whether Ollama is reachable
            - ollama_host: The Ollama host being tested
            - available_models: List of available models
            - embedding_model_available: Whether the configured model is available
            - configured_model: The configured embedding model name
            - error: Error details if connection fails
    """
    # Import environment variables from vector_store module
    ollama_host = config.OLLAMA_HOST
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
                            "embedding_model_available": config.OLLAMA_EMBEDDING_MODEL in model_names,
        "configured_model": config.OLLAMA_EMBEDDING_MODEL,
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
