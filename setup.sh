#!/bin/bash

# Canvas Quiz Manager Setup Script

echo "Setting up Canvas Quiz Manager..."

# Create project directory structure
mkdir -p templates
mkdir -p static
mkdir -p static/css
mkdir -p static/js

# Create the main application file
cat > main.py << 'EOF'
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
DATA_FILE = "quiz_questions.json"

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
    
    return templates.TemplateResponse("edit_question.html", {
        "request": request,
        "question": question
    })

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
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create templates directory and files
cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canvas Quiz Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .question-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        .question-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .question-text {
            max-height: 100px;
            overflow-y: auto;
        }
        .loading {
            display: none;
        }
        .question-type-badge {
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="h2"><i class="fas fa-question-circle text-primary"></i> Canvas Quiz Manager</h1>
                    <div>
                        <button id="fetchBtn" class="btn btn-primary">
                            <i class="fas fa-download"></i> Fetch Questions
                        </button>
                    </div>
                </div>

                <!-- Configuration Info -->
                <div class="alert alert-info mb-4">
                    <strong>Configuration:</strong> Course ID: {{ course_id }}, Quiz ID: {{ quiz_id }}
                </div>

                <!-- Loading indicator -->
                <div id="loading" class="text-center py-4 loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Fetching questions from Canvas...</p>
                </div>

                <!-- Alert container -->
                <div id="alertContainer"></div>

                <!-- Questions count -->
                {% if questions %}
                <div class="mb-3">
                    <span class="badge bg-secondary">{{ questions|length }} questions loaded</span>
                </div>
                {% endif %}

                <!-- Questions list -->
                <div class="row" id="questionsContainer">
                    {% if not questions %}
                    <div class="col-12">
                        <div class="alert alert-warning text-center">
                            <i class="fas fa-exclamation-triangle"></i>
                            No questions loaded. Click "Fetch Questions" to load from Canvas.
                        </div>
                    </div>
                    {% else %}
                    {% for question in questions %}
                    <div class="col-lg-6 col-xl-4 mb-4" data-question-id="{{ question.id }}">
                        <div class="card question-card h-100">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <span class="badge bg-primary question-type-badge">
                                    {{ question.question_type.replace('_', ' ').title() }}
                                </span>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a class="dropdown-item" href="/questions/{{ question.id }}">
                                            <i class="fas fa-edit"></i> Edit
                                        </a></li>
                                        <li><hr class="dropdown-divider"></li>
                                        <li><a class="dropdown-item text-danger delete-btn" href="#" data-question-id="{{ question.id }}">
                                            <i class="fas fa-trash"></i> Delete
                                        </a></li>
                                    </ul>
                                </div>
                            </div>
                            <div class="card-body" onclick="window.location.href='/questions/{{ question.id }}'">
                                <div class="question-text">
                                    {{ question.question_text | safe }}
                                </div>
                                <div class="mt-2">
                                    <small class="text-muted">
                                        <i class="fas fa-star"></i> {{ question.points_possible }} points
                                        {% if question.answers %}
                                        | <i class="fas fa-list"></i> {{ question.answers|length }} answers
                                        {% endif %}
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                    {% endif %}
                </div>
            </div>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirm Delete</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    Are you sure you want to delete this question? This action cannot be undone.
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" id="confirmDelete">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let questionToDelete = null;
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));

        // Fetch questions
        document.getElementById('fetchBtn').addEventListener('click', async () => {
            const loading = document.getElementById('loading');
            const fetchBtn = document.getElementById('fetchBtn');
            
            loading.style.display = 'block';
            fetchBtn.disabled = true;
            
            try {
                const response = await fetch('/fetch-questions', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showAlert('success', result.message);
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    showAlert('danger', result.detail || 'Failed to fetch questions');
                }
            } catch (error) {
                showAlert('danger', 'Error: ' + error.message);
            } finally {
                loading.style.display = 'none';
                fetchBtn.disabled = false;
            }
        });

        // Delete question
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('delete-btn') || e.target.closest('.delete-btn')) {
                e.preventDefault();
                const target = e.target.classList.contains('delete-btn') ? e.target : e.target.closest('.delete-btn');
                questionToDelete = target.dataset.questionId;
                deleteModal.show();
            }
        });

        document.getElementById('confirmDelete').addEventListener('click', async () => {
            if (!questionToDelete) return;
            
            try {
                const response = await fetch(`/questions/${questionToDelete}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showAlert('success', result.message);
                    document.querySelector(`[data-question-id="${questionToDelete}"]`).remove();
                    updateQuestionCount();
                } else {
                    showAlert('danger', result.detail || 'Failed to delete question');
                }
            } catch (error) {
                showAlert('danger', 'Error: ' + error.message);
            } finally {
                deleteModal.hide();
                questionToDelete = null;
            }
        });

        function showAlert(type, message) {
            const alertContainer = document.getElementById('alertContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-dismissible fade show`;
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            alertContainer.appendChild(alert);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }

        function updateQuestionCount() {
            const questionCards = document.querySelectorAll('.question-card').length;
            const badge = document.querySelector('.badge.bg-secondary');
            if (badge) {
                badge.textContent = `${questionCards} questions loaded`;
            }
        }
    </script>
</body>
</html>
EOF

cat > templates/edit_question.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Question - Canvas Quiz Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .form-control:focus {
            border-color: #0d6efd;
            box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
        }
        .answer-item {
            border: 1px solid #dee2e6;
            border-radius: 0.375rem;
            margin-bottom: 1rem;
            background-color: #f8f9fa;
        }
        .answer-weight {
            background-color: #e9ecef;
        }
        .feedback-section {
            background-color: #f8f9fa;
            border-radius: 0.375rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .auto-save-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="container-fluid py-4">
        <!-- Auto-save indicator -->
        <div id="autoSaveIndicator" class="auto-save-indicator" style="display: none;">
            <div class="alert alert-success alert-sm mb-0">
                <i class="fas fa-check"></i> Saved
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1 class="h2">
                        <i class="fas fa-edit text-primary"></i> Edit Question
                    </h1>
                    <a href="/" class="btn btn-outline-secondary">
                        <i class="fas fa-arrow-left"></i> Back to List
                    </a>
                </div>

                <form id="questionForm">
                    <!-- Question Basic Info -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-question-circle"></i> Question Details
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label"><strong>Question ID:</strong></label>
                                    <input type="text" class="form-control" value="{{ question.id }}" readonly>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label"><strong>Type:</strong></label>
                                    <input type="text" class="form-control" value="{{ question.question_type.replace('_', ' ').title() }}" readonly>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="questionText" class="form-label"><strong>Question Text:</strong></label>
                                <textarea id="questionText" name="question_text" class="form-control" rows="4">{{ question.question_text }}</textarea>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <label class="form-label"><strong>Points Possible:</strong></label>
                                    <input type="text" class="form-control" value="{{ question.points_possible }}" readonly>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label"><strong>Quiz ID:</strong></label>
                                    <input type="text" class="form-control" value="{{ question.quiz_id }}" readonly>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Question Feedback -->
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-comment"></i> Question Feedback
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="feedback-section">
                                <h6 class="text-success"><i class="fas fa-check-circle"></i> Correct Answer Feedback</h6>
                                <div class="mb-3">
                                    <label for="correctComments" class="form-label">Text:</label>
                                    <textarea id="correctComments" name="correct_comments" class="form-control" rows="2">{{ question.correct_comments }}</textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="correctCommentsHtml" class="form-label">HTML:</label>
                                    <textarea id="correctCommentsHtml" name="correct_comments_html" class="form-control" rows="2">{{ question.correct_comments_html }}</textarea>
                                </div>
                            </div>

                            <div class="feedback-section">
                                <h6 class="text-danger"><i class="fas fa-times-circle"></i> Incorrect Answer Feedback</h6>
                                <div class="mb-3">
                                    <label for="incorrectComments" class="form-label">Text:</label>
                                    <textarea id="incorrectComments" name="incorrect_comments" class="form-control" rows="2">{{ question.incorrect_comments }}</textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="incorrectCommentsHtml" class="form-label">HTML:</label>
                                    <textarea id="incorrectCommentsHtml" name="incorrect_comments_html" class="form-control" rows="2">{{ question.incorrect_comments_html }}</textarea>
                                </div>
                            </div>

                            <div class="feedback-section">
                                <h6 class="text-info"><i class="fas fa-info-circle"></i> Neutral/General Feedback</h6>
                                <div class="mb-3">
                                    <label for="neutralComments" class="form-label">Text:</label>
                                    <textarea id="neutralComments" name="neutral_comments" class="form-control" rows="2">{{ question.neutral_comments }}</textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="neutralCommentsHtml" class="form-label">HTML:</label>
                                    <textarea id="neutralCommentsHtml" name="neutral_comments_html" class="form-control" rows="2">{{ question.neutral_comments_html }}</textarea>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Answers -->
                    {% if question.answers %}
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-list"></i> Answers ({{ question.answers|length }})
                            </h5>
                        </div>
                        <div class="card-body">
                            <div id="answersContainer">
                                {% for answer in question.answers %}
                                <div class="answer-item p-3" data-answer-id="{{ answer.id }}">
                                    <div class="row mb-2">
                                        <div class="col-md-2">
                                            <label class="form-label">Weight:</label>
                                            <input type="number" name="answer_weight_{{ answer.id }}" class="form-control answer-weight" value="{{ answer.weight }}" step="0.1">
                                        </div>
                                        <div class="col-md-10">
                                            <label class="form-label">Answer Text:</label>
                                            <textarea name="answer_text_{{ answer.id }}" class="form-control" rows="2">{{ answer.text }}</textarea>
                                        </div>
                                    </div>
                                    
                                    {% if answer.html %}
                                    <div class="mb-2">
                                        <label class="form-label">HTML:</label>
                                        <textarea name="answer_html_{{ answer.id }}" class="form-control" rows="2">{{ answer.html }}</textarea>
                                    </div>
                                    {% endif %}

                                    <div class="row">
                                        <div class="col-md-6">
                                            <label class="form-label">Comments:</label>
                                            <textarea name="answer_comments_{{ answer.id }}" class="form-control" rows="2">{{ answer.comments }}</textarea>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">Comments HTML:</label>
                                            <textarea name="answer_comments_html_{{ answer.id }}" class="form-control" rows="2">{{ answer.comments_html }}</textarea>
                                        </div>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                    {% endif %}
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const questionId = {{ question.id }};
        let saveTimeout;
        let isSaving = false;

        // Auto-save functionality
        function scheduleAutoSave() {
            if (saveTimeout) {
                clearTimeout(saveTimeout);
            }
            saveTimeout = setTimeout(autoSave, 1000); // Save after 1 second of inactivity
        }

        async function autoSave() {
            if (isSaving) return;
            
            isSaving = true;
            const formData = collectFormData();
            
            try {
                const response = await fetch(`/questions/${questionId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    showAutoSaveIndicator();
                } else {
                    const error = await response.json();
                    console.error('Save failed:', error);
                }
            } catch (error) {
                console.error('Save error:', error);
            } finally {
                isSaving = false;
            }
        }

        function collectFormData() {
            const form = document.getElementById('questionForm');
            const formData = new FormData(form);
            
            // Collect basic question data
            const data = {
                question_text: formData.get('question_text') || '',
                correct_comments: formData.get('correct_comments') || '',
                incorrect_comments: formData.get('incorrect_comments') || '',
                neutral_comments: formData.get('neutral_comments') || '',
                correct_comments_html: formData.get('correct_comments_html') || '',
                incorrect_comments_html: formData.get('incorrect_comments_html') || '',
                neutral_comments_html: formData.get('neutral_comments_html') || '',
                answers: []
            };

            // Collect answers data
            const answerItems = document.querySelectorAll('.answer-item');
            answerItems.forEach(item => {
                const answerId = item.dataset.answerId;
                const answer = {
                    id: parseInt(answerId),
                    text: formData.get(`answer_text_${answerId}`) || '',
                    html: formData.get(`answer_html_${answerId}`) || '',
                    comments: formData.get(`answer_comments_${answerId}`) || '',
                    comments_html: formData.get(`answer_comments_html_${answerId}`) || '',
                    weight: parseFloat(formData.get(`answer_weight_${answerId}`)) || 0
                };
                data.answers.push(answer);
            });

            return data;
        }

        function showAutoSaveIndicator() {
            const indicator = document.getElementById('autoSaveIndicator');
            indicator.style.display = 'block';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 2000);
        }

        // Add event listeners for auto-save
        document.getElementById('questionForm').addEventListener('input', scheduleAutoSave);
        document.getElementById('questionForm').addEventListener('change', scheduleAutoSave);

        // Handle textarea changes
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', scheduleAutoSave);
            textarea.addEventListener('blur', scheduleAutoSave);
        });

        // Prevent form submission
        document.getElementById('questionForm').addEventListener('submit', (e) => {
            e.preventDefault();
        });
    </script>
</body>
</html>
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
jinja2==3.1.2
python-dotenv==1.0.0
httpx==0.25.2
pydantic==2.5.0
EOF

# Create .env template
cat > .env.template << 'EOF'
# Canvas API Configuration
CANVAS_BASE_URL=https://your-canvas-instance.instructure.com
CANVAS_API_TOKEN=your_canvas_api_token_here
COURSE_ID=your_course_id
QUIZ_ID=your_quiz_id

# Example values (replace with your actual values):
# CANVAS_BASE_URL=https://canvas.vt.edu
# CANVAS_API_TOKEN=1234~abcdefghijklmnopqrstuvwxyz
# COURSE_ID=123456
# QUIZ_ID=789012
EOF

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "Please edit .env file with your Canvas API credentials"
fi

# Create empty static files if needed
touch static/css/custom.css
touch static/js/custom.js

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your Canvas API credentials"
echo "2. Run the application with: python main.py"
echo "   or: uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo "3. Open your browser to: http://localhost:8000"
echo ""
echo "Files created:"
echo "- main.py (FastAPI application)"
echo "- templates/index.html (Questions list page)"
echo "- templates/edit_question.html (Question edit page)"
echo "- requirements.txt (Python dependencies)"
echo "- .env.template (Environment variables template)"
echo "- .env (Your configuration file - edit this!)"
echo ""
echo "The application will:"
echo "- Fetch questions from Canvas API with pagination"
echo "- Store questions in quiz_questions.json"
echo "- Allow editing questions and answers"
echo "- Auto-save changes"
echo "- Handle rate limiting with retry logic"
echo "- Log errors to canvas_app.log"