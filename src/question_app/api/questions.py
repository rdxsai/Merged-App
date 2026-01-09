"""
API endpoints for managing questions.
--- THIS IS THE FULLY CORRECTED VERSION ---
- Fixes the 'generate-feedback' TypeError
- Includes the 'suggest-objectives' endpoint
- FIX: Adds Markdown-to-HTML conversion for the preview
"""
import logging
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx 
import markdown # <-- 1. ADD THIS IMPORT
import uuid
from datetime import datetime


from ..core import config, get_logger
from ..services.database import DatabaseManager
from ..models import QuestionUpdate
from ..services.ai_service import AIGeneratorService 
from ..models import QuestionUpdate, NewQuestion

logger = get_logger(__name__)
router = APIRouter(prefix="/questions", tags=["questions"])
templates = Jinja2Templates(directory="templates")

# Initialize services
db = DatabaseManager(config.db_path)
ai_generator = AIGeneratorService()


@router.get("/new", response_class=HTMLResponse)
async def new_question_page(request: Request):
    """
    Serves the page for creating a new question.
    """
    logger.info("Loading new question creation page")
    try:
        all_objectives = db.list_all_objectives()
        
        # Create an empty question structure
        empty_question = {
            'id': 'new',  # Special marker for new questions
            'question_text': '',
            'question_text_html': '',
            'objective_ids': [],
            'answers': [
                {'id': 'new_1', 'text': '', 'text_html': '', 'is_correct': False, 'feedback_text': '', 'feedback_approved': False},
                {'id': 'new_2', 'text': '', 'text_html': '', 'is_correct': False, 'feedback_text': '', 'feedback_approved': False},
                {'id': 'new_3', 'text': '', 'text_html': '', 'is_correct': False, 'feedback_text': '', 'feedback_approved': False},
                {'id': 'new_4', 'text': '', 'text_html': '', 'is_correct': False, 'feedback_text': '', 'feedback_approved': False},
            ]
        }
        
        return templates.TemplateResponse(
            "edit_question.html",
            {
                "request": request,
                "question": empty_question,
                "all_objectives": all_objectives,
                "is_new": True  # Flag to tell template this is a new question
            },
        )
    except Exception as e:
        logger.error(f"Error loading new question page: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not load new question page.")


@router.post("/", response_class=JSONResponse)
async def create_question(data: NewQuestion):
    """
    Creates a new question in the database.
    Validates that question_text and at least one answer are provided.
    """
    logger.info("Creating new question")
    
    # Validation
    if not data.question_text or not data.question_text.strip():
        raise HTTPException(status_code=400, detail="Question text is required")
    
    if not data.answers or len(data.answers) == 0:
        raise HTTPException(status_code=400, detail="At least one answer is required")
    
    # Check if any answer text is provided
    if not any(answer.text.strip() for answer in data.answers):
        raise HTTPException(status_code=400, detail="At least one answer must have text")
    
    try:
        # Create new question with UUID
        new_question_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        with db.get_connection(use_row_factory=False) as conn:
            cursor = conn.cursor()
            
            # 1. Insert question
            cursor.execute(
                "INSERT INTO question (id, question_text, created_at) VALUES (?, ?, ?)",
                (new_question_id, data.question_text, created_at)
            )
            
            # 2. Insert answers (only ones with text)
            for answer in data.answers:
                if answer.text.strip():  # Only save answers with content
                    answer_id = str(uuid.uuid4())
                    cursor.execute(
                        """
                        INSERT INTO answer (id, question_id, text, is_correct, feedback_text, feedback_approved)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (answer_id, new_question_id, answer.text, answer.is_correct, '', False)
                    )
            
            # 3. Insert objective associations
            if data.objective_ids:
                for obj_id in data.objective_ids:
                    if obj_id:
                        assoc_id = str(uuid.uuid4())
                        cursor.execute(
                            "INSERT INTO question_objective_association (id, question_id, objective_id) VALUES (?, ?, ?)",
                            (assoc_id, new_question_id, obj_id)
                        )
            
            conn.commit()
        
        logger.info(f"Successfully created question {new_question_id}")
        return {
            "success": True, 
            "message": "Question created successfully",
            "question_id": new_question_id
        }
        
    except Exception as e:
        logger.error(f"Error creating question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create question")

@router.get("/{question_id}", response_class=HTMLResponse)
async def edit_question_page(request: Request, question_id: str):
    """
    Serves the edit page for a single question.
    """
    logger.info(f"Loading edit page for question_id: {question_id}")
    try:
        question_data = db.load_question_details(question_id)
        if not question_data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        all_objectives = db.list_all_objectives()
        
        # --- === 2. THIS IS THE FIX FOR THE BLANK PREVIEW === ---
        # The template 'edit_question.html' (your original one)
        # expects HTML-converted text. We must do that conversion here.
        
        md = markdown.Markdown(extensions=['fenced_code', 'codehilite'])
        
        # 1. Convert the main question text
        if question_data.get('question_text'):
            question_data['question_text_html'] = md.convert(question_data['question_text'])
        else:
            question_data['question_text_html'] = ''

        # 2. Convert the text for each answer
        for answer in question_data.get('answers', []):
            if answer.get('text'):
                answer['text_html'] = md.convert(answer['text'])
            else:
                answer['text_html'] = ''
        # --- === END OF FIX === ---
        
        return templates.TemplateResponse(
            "edit_question.html",
            {
                "request": request,
                "question": question_data,  # <-- This dict now has the _html fields
                "all_objectives": all_objectives,
            },
        )
    except Exception as e:
        logger.error(f"Error loading edit page: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not load edit page.")


@router.put("/{question_id}", response_class=JSONResponse)
async def save_question(question_id: str, data: QuestionUpdate, background_tasks: BackgroundTasks):
    """
    Saves updates to a question (auto-save).
    (This is the correct, working version)
    """
    try:
        success = db.update_question_and_answers(question_id, data)
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {"success": True, "message": "Question updated successfully"}
    except Exception as e:
        logger.error(f"Error saving question {question_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save question.")


@router.delete("/{question_id}", response_class=JSONResponse)
async def delete_question(question_id: str):
    """
    Deletes a question from the database.
    (This is the correct, working version)
    """
    try:
        success = db.delete_question(question_id)
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        return {"success": True, "message": "Question deleted."}
    except Exception as e:
        logger.error(f"Error deleting question {question_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete question.")


@router.post("/{question_id}/generate-feedback", response_class=JSONResponse)
async def generate_feedback_for_all_unapproved(question_id: str):
    """
    Generates AI feedback for all unapproved answers for a given question.
    (This is the correct, working version)
    """
    logger.info(f"Generating feedback request started for question {question_id}")
    
    try:
        question = db.load_question_details(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        updated_answers = []
        for answer in question.get("answers", []):
            if not answer.get("feedback_approved", False):
                logger.info(f"Generating feedback for unapproved answer_id: {answer['id']}")
                
                feedback_text = await ai_generator.generate_feedback_for_answer(
                    question_text=question['question_text'],
                    answer_text=answer['text'],
                    is_correct=answer['is_correct']
                )
                
                db.update_answer_feedback(answer['id'], feedback_text)
                updated_answers.append({
                    "answer_id": answer['id'],
                    "feedback_text": feedback_text
                })
        
        return {"success": True, "message": "Feedback generated.", "updated_answers": updated_answers}
    
    except httpx.HTTPStatusError as e:
        error_message = f"AI Service Error: {e}"
        if e.response.status_code == 429:
            error_message = "AI Service Error: Too many requests. Please wait and try again."
        elif e.response:
            try:
                error_detail = e.response.json()
                error_message = f"AI Error: {error_detail.get('error', {}).get('message', e)}"
            except Exception:
                pass 
        logger.error(f"Error in generate_feedback: {error_message}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_message)
    
    except Exception as e:
        logger.error(f"Error in generate_feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{question_id}/suggest-objectives", response_class=JSONResponse)
async def suggest_objectives(question_id: str):
    """
    (Req 8.2) Suggests existing objectives for a question using AI.
    (This is the correct, working version)
    """
    try:
        question = db.load_question_details(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        suggestions = await ai_generator.suggest_objectives_for_question(
            question['question_text']
        )
        
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error suggesting objectives: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to suggest objectives.")

