from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import json
import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import time
import random
import re
import chromadb
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('canvas_app.log'),
        logging.StreamHandler()
    ]
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
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://itls-openai-connect.azure-api.net")
AZURE_OPENAI_DEPLOYMENT_ID = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
AZURE_OPENAI_SUBSCRIPTION_KEY = os.getenv("AZURE_OPENAI_SUBSCRIPTION_KEY")

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# File paths
DATA_FILE = "quiz_questions.json"
SYSTEM_PROMPT_FILE = "system_prompt.txt"

# Pydantic models
class Answer(BaseModel):
    id: int
    text: str
    html: str = ""
    comments: str = ""
    comments_html: str = ""
    weight: float = 0.0

class Question(BaseModel):
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
    question_text: str
    correct_comments: str = ""
    incorrect_comments: str = ""
    neutral_comments: str = ""
    correct_comments_html: str = ""
    incorrect_comments_html: str = ""
    neutral_comments_html: str = ""
    answers: List[Answer] = []

# Utility functions
def load_questions() -> List[Dict[str, Any]]:
    """Load questions from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return []

def save_questions(questions: List[Dict[str, Any]]) -> bool:
    """Save questions to JSON file"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving questions: {e}")
        return False

def load_system_prompt() -> str:
    """Load system prompt from text file"""
    try:
        if os.path.exists(SYSTEM_PROMPT_FILE):
            with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return ""
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return ""

def save_system_prompt(prompt: str) -> bool:
    """Save system prompt to text file"""
    try:
        with open(SYSTEM_PROMPT_FILE, 'w', encoding='utf-8') as f:
            f.write(prompt)
        return True
    except Exception as e:
        logger.error(f"Error saving system prompt: {e}")
        return False

async def make_canvas_request(url: str, headers: Dict[str, str], max_retries: int = 3) -> Dict[str, Any]:
    """Make Canvas API request with retry logic for rate limiting"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    logger.warning(f"Rate limited, waiting {wait_time:.2f} seconds before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=e.response.status_code, detail=f"Canvas API error: {e}")
        except Exception as e:
            logger.error(f"Request error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail=f"Request failed: {e}")
    
    raise HTTPException(status_code=500, detail="Max retries exceeded")

def clean_question_text(text: str) -> str:
    """Remove unwanted HTML tags from question text, especially link and script tags"""
    if not text:
        return text
    
    # Remove link tags (CSS files)
    text = re.sub(r'<link[^>]*?>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove style tags and their content
    text = re.sub(r'<style[^>]*?>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove meta tags
    text = re.sub(r'<meta[^>]*?>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Clean up any extra whitespace that may have been left behind
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_html_for_vector_store(html_text: str) -> str:
    """Clean HTML tags and normalize text for vector store"""
    if not html_text:
        return ""
    
    # Parse HTML and extract text
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

async def get_ollama_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings from Ollama using nomic-embed-text model"""
    embeddings = []
    
    # Ensure OLLAMA_HOST has proper protocol
    ollama_host = OLLAMA_HOST
    if not ollama_host.startswith(('http://', 'https://')):
        ollama_host = f"http://{ollama_host}"
    
    logger.info(f"Using Ollama host: {ollama_host}")
    logger.info(f"Using embedding model: {OLLAMA_EMBEDDING_MODEL}")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            for i, text in enumerate(texts):
                payload = {
                    "model": OLLAMA_EMBEDDING_MODEL,
                    "prompt": text
                }
                
                logger.info(f"Generating embedding {i+1}/{len(texts)} (text length: {len(text)} chars)")
                
                url = f"{ollama_host}/api/embeddings"
                logger.debug(f"Making request to: {url}")
                
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"Ollama API error (status {response.status_code}): {error_text}")
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Ollama API error: {error_text}"
                    )
                
                result = response.json()
                
                if 'embedding' not in result:
                    logger.error(f"No embedding in Ollama response: {result}")
                    raise HTTPException(status_code=500, detail="Invalid response from Ollama - no embedding found")
                
                embeddings.append(result['embedding'])
                
                # Add small delay to avoid overwhelming Ollama
                await asyncio.sleep(0.1)
        
        logger.info(f"Generated {len(embeddings)} embeddings using Ollama {OLLAMA_EMBEDDING_MODEL} model")
        return embeddings
        
    except httpx.ConnectError as e:
        logger.error(f"Failed to connect to Ollama at {ollama_host}: {e}")
        raise HTTPException(
            status_code=503, 
            detail=f"Cannot connect to Ollama at {ollama_host}. Please ensure Ollama is running and the {OLLAMA_EMBEDDING_MODEL} model is installed."
        )
    except httpx.TimeoutException as e:
        logger.error(f"Ollama request timeout: {e}")
        raise HTTPException(status_code=408, detail="Ollama request timed out")
    except Exception as e:
        logger.error(f"Error generating embeddings with Ollama: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate embeddings: {str(e)}")

def create_comprehensive_chunks(questions: List[Dict[str, Any]]) -> tuple[List[str], List[Dict[str, Any]], List[str]]:
    """Create comprehensive chunks using Option C strategy"""
    documents = []
    metadatas = []
    ids = []
    
    for question in questions:
        # Extract and clean question text
        question_text = clean_html_for_vector_store(question.get('question_text', ''))
        question_type = question.get('question_type', '')
        general_feedback = clean_html_for_vector_store(question.get('neutral_comments', ''))
        
        # Build comprehensive document text
        doc_parts = []
        
        # Add question
        if question_text:
            doc_parts.append(f"Question: {question_text}")
        
        # Add question type context
        if question_type:
            doc_parts.append(f"Question Type: {question_type.replace('_', ' ').title()}")
        
        # Process answers
        correct_answers = []
        all_answers = []
        answer_feedback_parts = []
        
        for answer in question.get('answers', []):
            answer_text = clean_html_for_vector_store(answer.get('text', ''))
            weight = answer.get('weight', 0)
            is_correct = weight > 0
            answer_feedback = clean_html_for_vector_store(answer.get('comments', ''))
            
            if answer_text:
                status = "CORRECT" if is_correct else "INCORRECT"
                all_answers.append(f"- {answer_text} ({status})")
                
                if is_correct:
                    correct_answers.append(answer_text)
                
                # Add specific answer feedback if available
                if answer_feedback:
                    answer_feedback_parts.append(f"Feedback for '{answer_text}': {answer_feedback}")
        
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
            "question_id": question.get('id'),
            "question_type": question_type,
            "points_possible": float(question.get('points_possible', 0)),
            "correct_answers": " | ".join(correct_answers) if correct_answers else "",  # Convert list to string
            "answer_count": len(question.get('answers', [])),
            "has_feedback": bool(general_feedback),
            "topic": extract_topic_from_text(question_text, general_feedback)
        }
        
        documents.append(document_text)
        metadatas.append(metadata)
        ids.append(f"question_{question.get('id')}")
    
    return documents, metadatas, ids

def extract_topic_from_text(question_text: str, feedback: str = "") -> str:
    """Extract topic/theme from question text and feedback"""
    combined_text = f"{question_text} {feedback}".lower()
    
    # Simple keyword-based topic extraction
    topics = {
        "accessibility": ["accessibility", "screen reader", "alt text", "wcag", "disability", "inclusive"],
        "navigation": ["navigation", "menu", "link", "breadcrumb", "sitemap"],
        "forms": ["form", "input", "label", "validation", "submit"],
        "media": ["image", "video", "audio", "media", "caption", "transcript"],
        "color": ["color", "contrast", "visual", "design", "appearance"],
        "keyboard": ["keyboard", "focus", "tab", "shortcut", "navigation"],
        "content": ["content", "text", "heading", "structure", "semantic"]
    }
    
    for topic, keywords in topics.items():
        if any(keyword in combined_text for keyword in keywords):
            return topic
    
    return "general"

async def generate_feedback_with_ai(question_data: Dict[str, Any], system_prompt: str) -> Dict[str, Any]:
    """Generate feedback using Azure OpenAI"""
    logger.info(f"Starting AI feedback generation for question ID: {question_data.get('id', 'unknown')}")
    
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_ID, AZURE_OPENAI_SUBSCRIPTION_KEY]):
        missing_configs = []
        if not AZURE_OPENAI_ENDPOINT: missing_configs.append("AZURE_OPENAI_ENDPOINT")
        if not AZURE_OPENAI_DEPLOYMENT_ID: missing_configs.append("AZURE_OPENAI_DEPLOYMENT_ID")
        if not AZURE_OPENAI_SUBSCRIPTION_KEY: missing_configs.append("AZURE_OPENAI_SUBSCRIPTION_KEY")
        logger.error(f"Missing Azure OpenAI configuration: {', '.join(missing_configs)}")
        raise HTTPException(status_code=500, detail=f"Azure OpenAI configuration incomplete. Missing: {', '.join(missing_configs)}")
    
    # Construct the Azure OpenAI URL
    url = f"{AZURE_OPENAI_ENDPOINT}/us-east/deployments/{AZURE_OPENAI_DEPLOYMENT_ID}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
    logger.info(f"Azure OpenAI URL: {url}")
    
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_OPENAI_SUBSCRIPTION_KEY,
        "Content-Type": "application/json"
    }
    
    # Prepare question context for AI
    question_context = {
        "question_text": question_data.get("question_text", ""),
        "question_type": question_data.get("question_type", ""),
        "points_possible": question_data.get("points_possible", 0),
        "answers": []
    }
    
    # Include answer information
    for answer in question_data.get("answers", []):
        question_context["answers"].append({
            "text": answer.get("text", ""),
            "weight": answer.get("weight", 0),
            "is_correct": answer.get("weight", 0) > 0
        })
    
    # Create user message with question context
    user_message = f"""Please generate educational feedback for this web accessibility quiz question:

Question Type: {question_context['question_type']}
Question Text: {question_context['question_text']}
Points Possible: {question_context['points_possible']}

Answer Choices:
"""
    
    for i, answer in enumerate(question_context['answers'], 1):
        correct_indicator = "✓ CORRECT" if answer['is_correct'] else "✗ INCORRECT"
        user_message += f"{i}. {answer['text']} (Weight: {answer['weight']}%) [{correct_indicator}]\n"
    
    user_message += """
Please provide comprehensive educational feedback following these guidelines:

1. GENERAL FEEDBACK: 
   - Explain why this accessibility concept is important for creating inclusive web experiences
   - Describe how this relates to users with different types of disabilities
   - Reference relevant WCAG guidelines, success criteria, or accessibility standards
   - Connect to broader principles of inclusive design and user experience
   - Explain real-world implications and potential impact on users

2. ANSWER FEEDBACK: 
   For each answer choice, provide detailed educational explanations:
   
   **For CORRECT answers:**
   - Explain WHY this is the best practice for accessibility
   - Describe how it helps users with disabilities
   - Reference specific WCAG guidelines or standards it addresses
   - Provide implementation context and additional considerations
   
   **For INCORRECT answers:**
   - Explain WHY this approach creates accessibility barriers
   - Describe which user groups would be most affected
   - Reference WCAG guidelines or standards it violates
   - Suggest what the correct approach should be instead
   - Explain potential legal or compliance implications

Format your response as:
   Answer 1: [detailed educational feedback for first answer choice]
   Answer 2: [detailed educational feedback for second answer choice]
   [etc.]

Focus on educational value - help students understand the principles behind web accessibility, not just the mechanics.
"""
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }
    
    logger.info(f"Sending request to Azure OpenAI with payload keys: {list(payload.keys())}")
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
                    detail=f"AI service error (status {response.status_code}): {response_text}"
                )
            
            result = response.json()
            logger.info(f"Azure OpenAI response received successfully")
            logger.debug(f"Full response: {json.dumps(result, indent=2)}")
            
            if 'choices' not in result or not result['choices']:
                logger.error("No choices in Azure OpenAI response")
                raise HTTPException(status_code=500, detail="Invalid response from AI service - no choices")
            
            ai_response = result['choices'][0]['message']['content']
            logger.info(f"AI response content length: {len(ai_response)} characters")
            logger.debug(f"AI response content: {ai_response}")
            
            # Extract token usage information
            token_usage = {}
            if 'usage' in result:
                token_usage = {
                    "prompt_tokens": result['usage'].get('prompt_tokens', 0),
                    "completion_tokens": result['usage'].get('completion_tokens', 0),
                    "total_tokens": result['usage'].get('total_tokens', 0)
                }
                logger.info(f"Token usage - Prompt: {token_usage['prompt_tokens']}, "
                           f"Completion: {token_usage['completion_tokens']}, "
                           f"Total: {token_usage['total_tokens']}")
            
            # Parse the AI response to extract general feedback and answer-specific feedback
            feedback = {
                "general_feedback": "",
                "answer_feedback": {},
                "token_usage": token_usage
            }
            
            lines = ai_response.split('\n')
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
                if any(phrase in line.lower() for phrase in ['general feedback:', 'importance and relevance', '1. general feedback']):
                    current_section = 'general'
                    logger.info(f"Found general feedback section at line {line_num}")
                    # Extract content after colon if present
                    if ':' in line:
                        content = line.split(':', 1)[1].strip()
                        if content:
                            general_feedback_lines.append(content)
                elif any(phrase in line.lower() for phrase in ['answer feedback:', '2. answer feedback', 'answer 1:']):
                    current_section = 'answers'
                    logger.info(f"Found answer feedback section at line {line_num}")
                    # Check if this line contains answer feedback
                    if 'answer' in line.lower() and ':' in line:
                        if current_answer_key and current_answer_text:
                            feedback['answer_feedback'][current_answer_key] = ' '.join(current_answer_text)
                        
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = [parts[1].strip()] if parts[1].strip() else []
                            logger.debug(f"Found answer key: {current_answer_key}")
                elif current_section == 'general':
                    # Continue adding to general feedback
                    general_feedback_lines.append(line)
                elif current_section == 'answers':
                    # Check if this is a new answer
                    if 'answer' in line.lower() and ':' in line:
                        # Save previous answer if exists
                        if current_answer_key and current_answer_text:
                            feedback['answer_feedback'][current_answer_key] = ' '.join(current_answer_text)
                        
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            current_answer_key = parts[0].strip().lower()
                            current_answer_text = [parts[1].strip()] if parts[1].strip() else []
                            logger.debug(f"Found answer key: {current_answer_key}")
                    elif current_answer_key:
                        # Continue adding to current answer feedback
                        current_answer_text.append(line)
                elif not current_section:
                    # Before any section is found, assume it's general feedback
                    general_feedback_lines.append(line)
            
            # Save the last answer if exists
            if current_answer_key and current_answer_text:
                feedback['answer_feedback'][current_answer_key] = ' '.join(current_answer_text)
            
            # Combine general feedback lines
            feedback['general_feedback'] = ' '.join(general_feedback_lines)
            
            # If no structured parsing worked, put everything in general feedback
            if not feedback['general_feedback'] and not feedback['answer_feedback']:
                logger.warning("Failed to parse AI response into sections, using full response as general feedback")
                feedback['general_feedback'] = ai_response
            
            logger.info(f"Parsed feedback - General: {len(feedback['general_feedback'])} chars, "
                       f"Answer feedback entries: {len(feedback['answer_feedback'])}")
            
            return feedback
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Azure OpenAI HTTP error: {e}")
        logger.error(f"Response text: {e.response.text if hasattr(e, 'response') else 'No response text'}")
        raise HTTPException(status_code=e.response.status_code, detail=f"AI service HTTP error: {e}")
    except httpx.TimeoutException as e:
        logger.error(f"Azure OpenAI timeout error: {e}")
        raise HTTPException(status_code=408, detail="AI service request timed out")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Azure OpenAI response as JSON: {e}")
        raise HTTPException(status_code=500, detail="Invalid JSON response from AI service")
    except Exception as e:
        logger.error(f"Unexpected error generating feedback: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Failed to generate feedback: {str(e)}")

async def fetch_all_questions() -> List[Dict[str, Any]]:
    """Fetch all questions from Canvas API with pagination"""
    if not all([CANVAS_BASE_URL, CANVAS_API_TOKEN, COURSE_ID, QUIZ_ID]):
        raise HTTPException(status_code=500, detail="Missing Canvas configuration")
    
    headers = {
        "Authorization": f"Bearer {CANVAS_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    all_questions = []
    page = 1
    per_page = 100
    
    while True:
        url = f"{CANVAS_BASE_URL}/api/v1/courses/{COURSE_ID}/quizzes/{QUIZ_ID}/questions"
        params = f"?page={page}&per_page={per_page}"
        
        logger.info(f"Fetching page {page} from Canvas API")
        data = await make_canvas_request(url + params, headers)
        
        if not data:
            break
            
        # Clean question text from unwanted HTML tags
        for question in data:
            if 'question_text' in question and question['question_text']:
                question['question_text'] = clean_question_text(question['question_text'])
            
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
    """Home page showing all questions"""
    questions = load_questions()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "questions": questions,
        "course_id": COURSE_ID,
        "quiz_id": QUIZ_ID
    })

@app.post("/fetch-questions")
async def fetch_questions():
    """Fetch questions from Canvas API"""
    try:
        questions = await fetch_all_questions()
        if save_questions(questions):
            logger.info(f"Successfully saved {len(questions)} questions")
            return {"success": True, "message": f"Fetched and saved {len(questions)} questions"}
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
        questions = [q for q in questions if q.get('id') != question_id]
        
        if save_questions(questions):
            logger.info(f"Deleted question {question_id}")
            return {"success": True, "message": "Question deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save changes")
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/questions/{question_id}", response_class=HTMLResponse)
async def edit_question(request: Request, question_id: int):
    """Show question edit page"""
    questions = load_questions()
    question = next((q for q in questions if q.get('id') == question_id), None)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Find previous and next question IDs for navigation
    question_ids = [q.get('id') for q in questions]
    current_index = question_ids.index(question_id)
    
    prev_question_id = question_ids[current_index - 1] if current_index > 0 else None
    next_question_id = question_ids[current_index + 1] if current_index < len(question_ids) - 1 else None
    
    return templates.TemplateResponse("edit_question.html", {
        "request": request,
        "question": question,
        "prev_question_id": prev_question_id,
        "next_question_id": next_question_id,
        "current_position": current_index + 1,
        "total_questions": len(questions)
    })

@app.get("/system-prompt", response_class=HTMLResponse)
async def get_system_prompt_page(request: Request):
    """Get the system prompt editing page"""
    prompt = load_system_prompt()
    return templates.TemplateResponse("system_prompt_edit.html", {
        "request": request,
        "current_prompt": prompt
    })

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
            raise HTTPException(status_code=400, detail="No system prompt configured. Please set a system prompt first.")
        
        logger.info(f"System prompt loaded successfully (length: {len(system_prompt)} characters)")
        
        # Find the question
        logger.info(f"Loading questions to find question {question_id}...")
        questions = load_questions()
        logger.info(f"Loaded {len(questions)} questions from file")
        
        question = next((q for q in questions if q.get('id') == question_id), None)
        
        if not question:
            logger.error(f"Question {question_id} not found in dataset")
            raise HTTPException(status_code=404, detail="Question not found")
        
        logger.info(f"Found question: type={question.get('question_type')}, text_length={len(question.get('question_text', ''))}")
        logger.info(f"Question has {len(question.get('answers', []))} answers")
        
        # Generate feedback using AI
        logger.info("Starting AI feedback generation...")
        feedback = await generate_feedback_with_ai(question, system_prompt)
        logger.info("AI feedback generation completed successfully")
        
        # Update the question with generated feedback
        logger.info("Updating question with generated feedback...")
        question_index = next((i for i, q in enumerate(questions) if q.get('id') == question_id), None)
        if question_index is not None:
            logger.info(f"Found question at index {question_index}")
            
            # Update the general feedback
            questions[question_index]['neutral_comments'] = feedback['general_feedback']
            
            # Update answer-specific feedback
            for i, answer in enumerate(questions[question_index].get('answers', [])):
                # Try different keys to match the answer
                answer_keys_to_try = [
                    f"answer {i+1}",
                    f"answer{i+1}",
                    f"{i+1}",
                    str(i+1)
                ]
                
                for key in answer_keys_to_try:
                    if key in feedback['answer_feedback']:
                        answer['comments'] = feedback['answer_feedback'][key]
                        logger.info(f"Updated answer {i+1} feedback")
                        break
            
            logger.info("Saving updated questions to file...")
            if save_questions(questions):
                logger.info(f"Successfully generated and saved AI feedback for question {question_id}")
                return {
                    "success": True, 
                    "message": "Feedback generated successfully",
                    "feedback": feedback
                }
            else:
                logger.error("Failed to save questions to file")
                raise HTTPException(status_code=500, detail="Failed to save generated feedback")
        else:
            logger.error(f"Could not find question {question_id} for update")
            raise HTTPException(status_code=404, detail="Question not found for update")
            
    except HTTPException as e:
        # Re-raise HTTP exceptions (they're already properly formatted)
        logger.error(f"HTTP Exception in generate_question_feedback: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error generating feedback for question {question_id}: {e}")
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
        question = next((q for q in questions if q.get('id') == question_id), None)
        
        if not question:
            return {"error": "Question not found", "total_questions": len(questions)}
        
        return {
            "question_found": True,
            "question_id": question.get('id'),
            "question_type": question.get('question_type'),
            "question_text_length": len(question.get('question_text', '')),
            "answers_count": len(question.get('answers', [])),
            "has_correct_comments": bool(question.get('correct_comments')),
            "has_incorrect_comments": bool(question.get('incorrect_comments')),
            "has_neutral_comments": bool(question.get('neutral_comments')),
            "question_keys": list(question.keys()),
            "total_questions": len(questions)
        }
    except Exception as e:
        return {"error": str(e), "error_type": type(e).__name__}

@app.post("/create-vector-store")
async def create_vector_store():
    """Create ChromaDB vector store from quiz questions using Azure embeddings"""
    logger.info("=== Vector Store Creation Started ===")
    
    try:
        # Load questions
        logger.info("Loading questions from JSON file...")
        questions = load_questions()
        if not questions:
            raise HTTPException(status_code=400, detail="No questions found to create vector store")
        
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
            metadata={"description": "Quiz questions with comprehensive content"}
        )
        
        # Add documents to collection
        logger.info("Adding documents to ChromaDB collection...")
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        # Create summary statistics
        topic_counts = {}
        question_type_counts = {}
        
        for metadata in metadatas:
            topic = metadata.get('topic', 'unknown')
            question_type = metadata.get('question_type', 'unknown')
            
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            question_type_counts[question_type] = question_type_counts.get(question_type, 0) + 1
        
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
                "vector_store_path": "./vector_store"
            }
        }
        
    except HTTPException as e:
        logger.error(f"HTTP Exception in create_vector_store: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating vector store: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Failed to create vector store: {str(e)}")

@app.get("/test-system-prompt", response_class=HTMLResponse)
async def test_system_prompt_page(request: Request):
    """Test page for system prompt functionality"""
    return templates.TemplateResponse("test_system_prompt.html", {"request": request})

@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration"""
    return {
        "canvas_configured": bool(CANVAS_BASE_URL and CANVAS_API_TOKEN and COURSE_ID and QUIZ_ID),
        "azure_configured": bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT_ID and AZURE_OPENAI_SUBSCRIPTION_KEY),
        "has_system_prompt": bool(load_system_prompt()),
        "data_file_exists": os.path.exists(DATA_FILE),
        "questions_count": len(load_questions()) if os.path.exists(DATA_FILE) else 0,
        "azure_endpoint": AZURE_OPENAI_ENDPOINT,
        "azure_deployment_id": AZURE_OPENAI_DEPLOYMENT_ID,
        "azure_api_version": AZURE_OPENAI_API_VERSION,
        "ollama_host": OLLAMA_HOST,
        "ollama_embedding_model": OLLAMA_EMBEDDING_MODEL,
        "ollama_host_with_protocol": OLLAMA_HOST if OLLAMA_HOST.startswith(('http://', 'https://')) else f"http://{OLLAMA_HOST}"
    }

@app.get("/debug/ollama-test")
async def test_ollama_connection():
    """Test Ollama connection and model availability"""
    ollama_host = OLLAMA_HOST
    if not ollama_host.startswith(('http://', 'https://')):
        ollama_host = f"http://{ollama_host}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test basic connection
            response = await client.get(f"{ollama_host}/api/tags")
            
            if response.status_code == 200:
                models = response.json()
                model_names = [model['name'] for model in models.get('models', [])]
                
                return {
                    "ollama_connected": True,
                    "ollama_host": ollama_host,
                    "available_models": model_names,
                    "embedding_model_available": OLLAMA_EMBEDDING_MODEL in model_names,
                    "configured_model": OLLAMA_EMBEDDING_MODEL
                }
            else:
                return {
                    "ollama_connected": False,
                    "error": f"Ollama returned status {response.status_code}",
                    "ollama_host": ollama_host
                }
                
    except httpx.ConnectError as e:
        return {
            "ollama_connected": False,
            "error": f"Cannot connect to Ollama at {ollama_host}",
            "ollama_host": ollama_host,
            "details": str(e)
        }
    except Exception as e:
        return {
            "ollama_connected": False,
            "error": f"Unexpected error: {str(e)}",
            "ollama_host": ollama_host
        }

@app.put("/questions/{question_id}")
async def update_question(question_id: int, question_data: QuestionUpdate):
    """Update a question"""
    try:
        questions = load_questions()
        question_index = next((i for i, q in enumerate(questions) if q.get('id') == question_id), None)
        
        if question_index is None:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Update the question
        questions[question_index].update({
            'question_text': question_data.question_text,
            'correct_comments': question_data.correct_comments,
            'incorrect_comments': question_data.incorrect_comments,
            'neutral_comments': question_data.neutral_comments,
            'correct_comments_html': question_data.correct_comments_html,
            'incorrect_comments_html': question_data.incorrect_comments_html,
            'neutral_comments_html': question_data.neutral_comments_html,
            'answers': [answer.dict() for answer in question_data.answers]
        })
        
        if save_questions(questions):
            logger.info(f"Updated question {question_id}")
            return {"success": True, "message": "Question updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save changes")
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)