"""
Canvas API endpoints and utilities.

This module contains all Canvas LMS integration endpoints including:
- Course management
- Quiz management  
- Question fetching
- Configuration management
"""

import asyncio
import logging
import os
import random
import re
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["canvas"])

# Configuration from environment
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")
COURSE_ID = os.getenv("COURSE_ID")
QUIZ_ID = os.getenv("QUIZ_ID")


class ConfigurationUpdate(BaseModel):
    """Model for configuration update requests."""
    course_id: str = None
    quiz_id: str = None


class FetchQuestionsResponse(BaseModel):
    """Model for fetch questions response."""
    success: bool
    message: str


async def make_canvas_request(
    url: str, headers: Dict[str, str], max_retries: int = 3
) -> Dict[str, Any]:
    """
    Make a Canvas API request with retry logic for rate limiting.

    Args:
        url (str): The Canvas API endpoint URL to request.
        headers (Dict[str, str]): HTTP headers to include in the request.
        max_retries (int, optional): Maximum number of retry attempts.
            Defaults to 3.

    Returns:
        Dict[str, Any]: JSON response from the Canvas API.

    Raises:
        HTTPException: If the request fails after all retry attempts or if
            the API returns an error status code.

    Note:
        This function implements exponential backoff for rate limiting (429
        errors) and includes proper error handling for various HTTP status
        codes.
    """
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)

                if response.status_code == 429:  # Rate limited
                    wait_time = 2**attempt + random.uniform(0, 1)
                    logger.warning(
                        f"Rate limited, waiting {wait_time:.2f} seconds "
                        f"before retry {attempt + 1}"
                    )
                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Canvas API error: {e}"
                )
        except Exception as e:
            logger.error(f"Request error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=500, detail=f"Request failed: {e}"
                )

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
        r"<script[^>]*?>.*?</script>", "",
        text, flags=re.IGNORECASE | re.DOTALL
    )

    # Remove style tags and their content
    text = re.sub(
        r"<style[^>]*?>.*?</style>", "",
        text, flags=re.IGNORECASE | re.DOTALL
    )

    # Remove meta tags
    text = re.sub(r"<meta[^>]*?>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Clean up any extra whitespace that may have been left behind
    text = re.sub(r"\s+", " ", text).strip()

    return text


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


# Import data management functions from utils module
# These are imported from the utils package for consistency
def load_questions() -> List[Dict[str, Any]]:
    """Load questions from the data file."""
    import json
    from pathlib import Path
    
    data_file = Path("data/quiz_questions.json")
    if data_file.exists():
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading questions: {e}")
    return []


def save_questions(questions: List[Dict[str, Any]]) -> bool:
    """Save questions to the data file."""
    import json
    from pathlib import Path
    
    try:
        data_file = Path("data/quiz_questions.json")
        data_file.parent.mkdir(exist_ok=True)
        
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving questions: {e}")
        return False


@router.get("/courses")
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


@router.get("/courses/{course_id}/quizzes")
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


@router.post("/configuration")
async def update_configuration(config_data: ConfigurationUpdate):
    """Update course and quiz configuration"""
    try:
        global COURSE_ID, QUIZ_ID

        if config_data.course_id:
            COURSE_ID = str(config_data.course_id)
        if config_data.quiz_id:
            QUIZ_ID = str(config_data.quiz_id)

        logger.info(
            f"Updated configuration: Course ID = {COURSE_ID}, Quiz ID = {QUIZ_ID}"
        )
        return {"success": True, "message": "Configuration updated successfully"}

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-questions")
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
