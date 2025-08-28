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

import json
import logging
import os
import re
from typing import Any, Dict, List

import httpx
import uvicorn
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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
from .api import canvas_router, questions_router, chat_router

# Import utility functions from organized modules
from .utils import (
    load_questions,
    save_questions,
    load_objectives,
    save_objectives,
    load_system_prompt,
    save_system_prompt,
    clean_answer_feedback,
    get_all_existing_tags,
)

app = FastAPI(title="Canvas Quiz Manager")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(canvas_router)
app.include_router(questions_router)
app.include_router(chat_router)

# Configuration from environment
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
COURSE_ID = os.getenv("COURSE_ID")
QUIZ_ID = os.getenv("QUIZ_ID")

# File paths
DATA_FILE = "data/quiz_questions.json"
SYSTEM_PROMPT_FILE = "config/system_prompt.txt"


# Import models from the models package
from .models import ObjectivesUpdate









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
    # Import environment variables from chat module
    from .api.chat import (
        AZURE_OPENAI_ENDPOINT,
        AZURE_OPENAI_DEPLOYMENT_ID,
        AZURE_OPENAI_SUBSCRIPTION_KEY,
        AZURE_OPENAI_API_VERSION,
        OLLAMA_HOST,
        OLLAMA_EMBEDDING_MODEL,
    )
    
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
    # Import environment variables from chat module
    from .api.chat import OLLAMA_HOST, OLLAMA_EMBEDDING_MODEL
    
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
