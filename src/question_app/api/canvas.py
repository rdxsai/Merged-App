"""
Canvas API endpoints and utilities.

This module contains all Canvas LMS integration endpoints including:
- Course management
- Quiz management  
- Question fetching
- Configuration management
"""

import asyncio
import html
import random
import re
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup

from ..core import config, get_logger

# Configure logging
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["canvas"])


class ConfigurationUpdate(BaseModel):
    """Model for configuration update requests."""

    course_id: Optional[str] = None
    quiz_id: Optional[str] = None


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
                    status_code=e.response.status_code, detail=f"Canvas API error: {e}"
                )
        except Exception as e:
            logger.error(f"Request error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"Request failed: {e}")

    raise HTTPException(status_code=500, detail="Max retries exceeded")


# Compiled regex patterns for performance
_INLINE_CODE_PATTERNS = {
    'html_tags': re.compile(r'(?<!`)<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>(?!`)', re.IGNORECASE),
    'html_attributes': re.compile(r'(?<!`)(\b(?:aria-|data-)?[a-zA-Z-]+\s*=\s*["\'][^"\']*["\'])(?!`)', re.IGNORECASE),
    'css_selectors': re.compile(r'(?<!`)([.#][a-zA-Z][a-zA-Z0-9_-]*|\[[^\]]+\])(?!`)', re.IGNORECASE),
    'html_entities': re.compile(r'&lt;([a-zA-Z][a-zA-Z0-9]*)\b[^&]*&gt;', re.IGNORECASE),
    'technical_terms': re.compile(r'\b([a-zA-Z][a-zA-Z0-9]*)\s+(element|tag|attribute|property)\b', re.IGNORECASE)
}

def _classify_content_type(soup: BeautifulSoup, original_text: str) -> str:
    """
    Enhanced classification system to distinguish between different content types.
    
    Returns: 'code_sample', 'mixed_content', 'formatted_text', or 'inline_mentions'
    """
    # Get text content for analysis
    text_content = soup.get_text().lower()
    
    # Count different types of elements
    structural_elements = soup.find_all(['div', 'form', 'input', 'button', 'select', 'textarea', 'table', 'tr', 'td', 'fieldset', 'legend'])
    formatting_elements = soup.find_all(['strong', 'em', 'b', 'i', 'code', 'a', 'ul', 'ol', 'li'])
    semantic_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote'])
    
    # Check for question context clues
    question_indicators = ['what is wrong', 'which is better', 'what should', 'how to', 'why', 'when to use']
    has_question_context = any(indicator in text_content for indicator in question_indicators)
    
    # Analyze content structure
    total_elements = len(structural_elements) + len(formatting_elements) + len(semantic_elements)
    structural_ratio = len(structural_elements) / max(total_elements, 1)
    
    # Check for inline code patterns in original text
    inline_code_count = sum(len(pattern.findall(original_text)) for pattern in _INLINE_CODE_PATTERNS.values())
    
    # Classification logic
    if len(structural_elements) >= 3 or (len(structural_elements) >= 2 and structural_ratio > 0.4):
        return 'code_sample'
    elif len(structural_elements) >= 1 and has_question_context and inline_code_count > 0:
        return 'mixed_content'
    elif len(formatting_elements) > 0 or len(semantic_elements) > 1:
        return 'formatted_text'
    else:
        return 'inline_mentions'


def _add_inline_code_formatting(text: str) -> str:
    """
    Add inline code formatting to technical terms and HTML references.
    
    Handles HTML tags, attributes, CSS selectors, ARIA patterns, and technical terms.
    """
    if not text or '`' in text:  # Skip if already has backticks
        return text
    
    try:
        # Decode HTML entities first
        text = html.unescape(text)
        
        # Pattern 1: HTML entities like &lt;div&gt; → `<div>`
        text = _INLINE_CODE_PATTERNS['html_entities'].sub(r'`<\1>`', text)
        
        # Pattern 2: HTML tags like <button> → `<button>`
        def format_html_tag(match):
            tag = match.group(0)
            # Don't format if it looks like actual HTML structure (has content after >)
            if '>' in tag and not tag.endswith('>'):
                return tag
            return f'`{tag}`'
        
        text = _INLINE_CODE_PATTERNS['html_tags'].sub(format_html_tag, text)
        
        # Pattern 3: HTML attributes like role="button" → `role="button"`
        text = _INLINE_CODE_PATTERNS['html_attributes'].sub(r'`\1`', text)
        
        # Pattern 4: CSS selectors like .class, #id → `.class`, `#id`
        text = _INLINE_CODE_PATTERNS['css_selectors'].sub(r'`\1`', text)
        
        # Pattern 5: Technical terms like "button element" → "`<button>` element"
        def format_technical_term(match):
            element_name = match.group(1).lower()
            term_type = match.group(2).lower()
            if term_type in ['element', 'tag']:
                return f'`<{element_name}>` {term_type}'
            return match.group(0)
        
        text = _INLINE_CODE_PATTERNS['technical_terms'].sub(format_technical_term, text)
        
        # Clean up common formatting artifacts
        text = re.sub(r'`{2,}', '`', text)  # Remove double backticks
        text = re.sub(r'`\s*`', '', text)   # Remove empty backticks
        
        return text
        
    except Exception as e:
        logger.warning(f"Error in inline code formatting: {e}")
        return text


def _convert_html_to_markdown(soup: BeautifulSoup) -> str:
    """
    Enhanced HTML to Markdown converter with comprehensive element handling.
    
    Handles all standard HTML elements with proper nesting and edge cases.
    """
    try:
        # Handle pre/code blocks first (preserve existing formatting)
        for pre in soup.find_all('pre'):
            code_content = pre.get_text()
            if code_content.strip():
                pre.replace_with(f"\n```\n{code_content}\n```\n")
            else:
                pre.decompose()
        
        # Handle standalone code elements (not in pre)
        for code in soup.find_all('code'):
            if not code.find_parent('pre'):  # Only if not already in a pre block
                code_text = code.get_text()
                if code_text.strip():
                    code.replace_with(f"`{code_text}`")
        
        # Convert headings (preserve hierarchy)
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                heading_text = heading.get_text().strip()
                if heading_text:
                    heading.replace_with(f"\n{'#' * i} {heading_text}\n")
        
        # Convert formatting elements
        for strong in soup.find_all(['strong', 'b']):
            strong_text = strong.get_text()
            if strong_text.strip():
                strong.replace_with(f"**{strong_text}**")
        
        for em in soup.find_all(['em', 'i']):
            em_text = em.get_text()
            if em_text.strip():
                em.replace_with(f"*{em_text}*")
        
        # Convert links (preserve href)
        for link in soup.find_all('a'):
            href = link.get('href', '').strip()
            text = link.get_text().strip()
            if text:
                if href and href != '#':
                    link.replace_with(f"[{text}]({href})")
                else:
                    link.replace_with(text)
        
        # Convert lists (handle nesting)
        for ul in soup.find_all('ul'):
            items = []
            for li in ul.find_all('li', recursive=False):
                li_text = li.get_text().strip()
                if li_text:
                    items.append(f"- {li_text}")
            if items:
                ul.replace_with('\n' + '\n'.join(items) + '\n')
        
        for ol in soup.find_all('ol'):
            items = []
            for i, li in enumerate(ol.find_all('li', recursive=False), 1):
                li_text = li.get_text().strip()
                if li_text:
                    items.append(f"{i}. {li_text}")
            if items:
                ol.replace_with('\n' + '\n'.join(items) + '\n')
        
        # Convert paragraphs (preserve structure)
        for p in soup.find_all('p'):
            p_text = p.get_text().strip()
            if p_text:
                p.replace_with(f"\n{p_text}\n")
        
        # Get final text and clean up
        result = soup.get_text()
        
        # Normalize whitespace
        result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)  # Max 2 consecutive newlines
        result = re.sub(r'[ \t]+', ' ', result)  # Normalize spaces
        result = result.strip()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in HTML to Markdown conversion: {e}")
        return soup.get_text().strip()


def clean_question_text(text: str) -> str:
    """
    Comprehensive Canvas HTML quiz question to Markdown converter.

    Intelligently handles different content types:
    - Inline code mentions: HTML tags/attributes in regular text → `<button>`, `role="application"`
    - Formatted text: HTML formatting → Markdown (strong → **bold**, em → *italic*)
    - Code samples: Substantial HTML structures → fenced code blocks
    - Mixed content: Separates instructional text from code demonstrations

    Args:
        text (str): Raw HTML from Canvas quiz question

    Returns:
        str: Clean Markdown with appropriate inline code and formatting

    Examples:
        Inline mentions: 'Use <button> instead of <span>' → 'Use `<button>` instead of `<span>`'
        Formatted text: '<strong>Important:</strong> use <code>aria-label</code>' → '**Important:** use `aria-label`'
        Code sample: 'Fix this: <div><input type="text"></div>' → 'Fix this:\n\n```html\n<div><input type="text"></div>\n```'
        HTML entities: '&lt;div&gt; element' → '`<div>` element'
    """
    if not text:
        return text

    try:
        # Store original text for pattern analysis
        original_text = text
        
        # Parse the HTML
        soup = BeautifulSoup(text, 'html.parser')

        # Remove unwanted elements but preserve content structure
        for unwanted in soup(['script', 'style', 'link', 'meta']):
            unwanted.decompose()

        # Clean up cosmetic spans while preserving semantic ones
        for span in soup.find_all('span'):
            has_semantic_attrs = (
                span.get('id') or 
                span.get('role') or 
                any(attr.startswith('aria-') for attr in span.attrs.keys())
            )
            
            is_cosmetic = (
                span.get('style') or 
                (span.get('class') and any('hljs' in cls for cls in span.get('class', [])))
            )
            
            if is_cosmetic and not has_semantic_attrs:
                span.replace_with(span.get_text())
                logger.debug("Removed cosmetic span")
            elif has_semantic_attrs:
                logger.debug(f"Preserved semantic span with id={span.get('id')}")

        # Remove style attributes and hljs classes
        for element in soup.find_all():
            if element.get('style'):
                del element['style']
            if element.get('class'):
                classes = [c for c in element.get('class', []) if not c.startswith('hljs')]
                if classes:
                    element['class'] = classes
                else:
                    del element['class']

        # Enhanced content classification
        content_type = _classify_content_type(soup, original_text)
        logger.debug(f"Content classified as: {content_type}")
        
        if content_type == 'code_sample':
            # Handle substantial code demonstrations
            result_parts = []
            processed_elements = set()
            
            for element in soup.find_all(['p', 'div', 'pre', 'code', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                if element in processed_elements or any(ancestor in processed_elements for ancestor in element.parents):
                    continue
                
                inner_html = ''.join(str(child) for child in element.children)
                
                # Check if this element contains structural HTML
                has_structural_html = bool(re.search(r'<(div|form|input|button|select|textarea|table|fieldset)[^>]*>', inner_html, re.IGNORECASE))
                
                if element.name in ['pre', 'code'] or has_structural_html:
                    # This is a code block
                    if element.name in ['pre', 'code']:
                        code_content = element.get_text().strip()
                    else:
                        code_content = inner_html.strip()
                    
                    if code_content:
                        result_parts.append(f"```html\n{code_content}\n```")
                        logger.debug(f"Added code block from <{element.name}>")
                else:
                    # This is instructional text - apply inline code formatting
                    text_content = element.get_text().strip()
                    if text_content:
                        formatted_text = _add_inline_code_formatting(text_content)
                        result_parts.append(formatted_text)
                        logger.debug(f"Added instruction text from <{element.name}>")
                
                processed_elements.add(element)
                for child in element.find_all():
                    processed_elements.add(child)
            
            return '\n\n'.join(result_parts) if result_parts else _add_inline_code_formatting(soup.get_text().strip())
        
        elif content_type == 'mixed_content':
            # Handle questions with both text and code elements
            markdown_text = _convert_html_to_markdown(soup)
            formatted_text = _add_inline_code_formatting(markdown_text)
            
            # Clean up whitespace
            formatted_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', formatted_text)
            formatted_text = re.sub(r'[ \t]+', ' ', formatted_text)
            
            return formatted_text.strip()
        
        elif content_type == 'formatted_text':
            # Handle regular questions with HTML formatting
            markdown_text = _convert_html_to_markdown(soup)
            
            # Apply inline code formatting to any technical terms
            formatted_text = _add_inline_code_formatting(markdown_text)
            
            # Clean up whitespace
            formatted_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', formatted_text)
            formatted_text = re.sub(r'[ \t]+', ' ', formatted_text)
            
            return formatted_text.strip()
        
        else:  # inline_mentions
            # Handle questions with just inline code references
            plain_text = soup.get_text().strip()
            formatted_text = _add_inline_code_formatting(plain_text)
            
            return formatted_text
            
    except Exception as e:
        logger.error(f"Error in clean_question_text: {e}")
        # Fallback to basic processing
        try:
            soup = BeautifulSoup(text, 'html.parser')
            for unwanted in soup(['script', 'style', 'link', 'meta']):
                unwanted.decompose()
            return _add_inline_code_formatting(soup.get_text().strip())
        except:
            return text.strip()


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
    if not config.validate_canvas_config():
        missing_configs = config.get_missing_canvas_configs()
        logger.error(f"Missing Canvas configuration: {', '.join(missing_configs)}")
        raise HTTPException(
            status_code=400,
            detail=f"Canvas API configuration incomplete. Missing: {', '.join(missing_configs)}",
        )

    headers = {"Authorization": f"Bearer {config.CANVAS_API_TOKEN}"}
    courses = []

    try:
        url = f"{config.CANVAS_BASE_URL}/api/v1/courses"
        params: Dict[str, Union[str, int]] = {
            "enrollment_state": "active",
            "per_page": 100,
            "include": "term",
        }

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
    if not config.validate_canvas_config():
        missing_configs = config.get_missing_canvas_configs()
        logger.error(f"Missing Canvas configuration: {', '.join(missing_configs)}")
        raise HTTPException(
            status_code=400,
            detail=f"Canvas API configuration incomplete. Missing: {', '.join(missing_configs)}",
        )

    headers = {"Authorization": f"Bearer {config.CANVAS_API_TOKEN}"}
    quizzes = []

    try:
        url = f"{config.CANVAS_BASE_URL}/api/v1/courses/{course_id}/quizzes"
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
    if not config.validate_canvas_config():
        missing_configs = config.get_missing_canvas_configs()
        raise HTTPException(
            status_code=500,
            detail=f"Missing Canvas configuration: {', '.join(missing_configs)}",
        )

    headers = {
        "Authorization": f"Bearer {config.CANVAS_API_TOKEN}",
        "Content-Type": "application/json",
    }

    all_questions: List[Dict[str, Any]] = []
    page = 1
    per_page = 100

    while True:
        url = f"{config.CANVAS_BASE_URL}/api/v1/courses/{config.COURSE_ID}/quizzes/{config.QUIZ_ID}/questions"
        params = f"?page={page}&per_page={per_page}"

        logger.info(f"Fetching page {page} from Canvas API")
        data = await make_canvas_request(url + params, headers)

        if not data:
            break

        # Clean question text from unwanted HTML tags
        for question in data:
            if (
                isinstance(question, dict)
                and "question_text" in question
                and isinstance(question["question_text"], str)  # type: ignore[index]
                and question["question_text"]  # type: ignore[index]
            ):
                question["question_text"] = clean_question_text(
                    question["question_text"]  # type: ignore[index]
                )  # type: ignore[index]

        all_questions.extend(data if isinstance(data, list) else [data])

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


@router.get("/configuration")
async def get_configuration():
    """Get current course and quiz configuration"""
    try:
        return {
            "success": True,
            "course_id": config.COURSE_ID,
            "quiz_id": config.QUIZ_ID,
            "canvas_base_url": config.CANVAS_BASE_URL,
        }
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configuration")
async def update_configuration(config_data: ConfigurationUpdate):
    """Update course and quiz configuration"""
    try:
        if config_data.course_id:
            config.COURSE_ID = str(config_data.course_id)
        if config_data.quiz_id:
            config.QUIZ_ID = str(config_data.quiz_id)

        logger.info(
            f"Updated configuration: Course ID = {config.COURSE_ID}, Quiz ID = {config.QUIZ_ID}"
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
