"""
Learning objectives management API endpoints.
--- THIS IS THE FINAL, CORRECTED VERSION ---
(With the 'draft' endpoints and NEW LOGGING)
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError # Import ValidationError
from typing import List

from ..core import get_logger, config
from ..services.database import DatabaseManager
from ..services.ai_service import AIGeneratorService

from ..models.objective import (
    ObjectiveCreate, 
    ObjectiveUpdate, 
    ObjectiveInDB,
    QuestionDraft
)

logger = get_logger(__name__)
router = APIRouter(prefix="/objectives", tags=["objectives"])
templates = Jinja2Templates(directory="templates")

db = DatabaseManager(config.db_path)
ai_generator = AIGeneratorService()

@router.get("/", response_class=HTMLResponse)
async def objectives_page(request: Request):
    """ (Unchanged) Learning objectives management page. """
    try:
        objectives = db.list_all_objectives_with_counts() 
        return templates.TemplateResponse(
            "objectives.html", {"request": request, "objectives": objectives}
        )
    except Exception as e:
        logger.error(f"Error loading objectives page: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not load objectives.")


@router.get("/list", response_class=JSONResponse)
async def list_all_objectives_json():
    """ Returns all objectives as JSON with full text. """
    try:
        objectives = db.list_all_objectives()
        return {"objectives": objectives}
    except Exception as e:
        logger.error(f"Error listing objectives: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch objectives.")


@router.post("/", response_class=JSONResponse)
async def create_new_objective(objective_data: ObjectiveCreate):
    """ Creates a single new learning objective and returns it as JSON. """
    try:
        new_obj_dict = db.create_objective(
            text=objective_data.text,
            blooms_level='understand',
            priority='medium'
        )
        objective = ObjectiveInDB.model_validate(new_obj_dict)
        return objective.model_dump()  # Return as JSON dict
    except Exception as e:
        logger.error(f"Error creating objective: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create objective.")


@router.put("/{objective_id}", response_class=JSONResponse)
async def update_existing_objective(objective_id: str, objective_data: ObjectiveUpdate):
    """ (Unchanged) Updates an existing objective. """
    try:
        success = db.update_objective(
            objective_id,
            objective_data.text,
            objective_data.blooms_level,
            objective_data.priority
        )
        if not success:
            raise HTTPException(status_code=404, detail="Objective not found.")
        return {"success": True, "message": "Objective updated."}
    except Exception as e:
        logger.error(f"Error updating objective {objective_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update objective.")


@router.delete("/{objective_id}", response_class=JSONResponse)
async def delete_existing_objective(objective_id: str):
    """ (Unchanged) Deletes an existing objective. """
    try:
        success = db.delete_objective(objective_id)
        if not success:
            raise HTTPException(status_code=404, detail="Objective not found.")
        return {"success": True, "message": "Objective deleted."}
    except Exception as e:
        logger.error(f"Error deleting objective {objective_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete objective.")


@router.post("/{objective_id}/generate-question-draft", response_class=JSONResponse)
async def generate_question_draft_for_objective(objective_id: str):
    """ (Unchanged) Calls the AI to generate a DRAFT of a question. """
    try:
        objective = db.get_objective(objective_id)
        if not objective:
            raise HTTPException(status_code=404, detail="Objective not found")
        
        ai_draft_json = await ai_generator.generate_question_from_objective(objective['text'])
        
        return ai_draft_json
    except Exception as e:
        logger.error(f"Error generating question draft: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) # Pass full error


@router.post("/{objective_id}/generate-and-create-question", response_class=JSONResponse)
async def generate_and_create_question_for_objective(objective_id: str):
    """
    Generates a question using AI and immediately creates it in the database.
    Returns the new question ID for redirect to edit page.
    """
    try:
        objective = db.get_objective(objective_id)
        if not objective:
            raise HTTPException(status_code=404, detail="Objective not found")
        
        # Generate AI draft
        ai_draft_json = await ai_generator.generate_question_from_objective(objective['text'])
        
        # Immediately create question in DB
        new_question_id = db.create_question_from_ai(
            question_data=ai_draft_json,
            objective_id=objective_id
        )
        
        if not new_question_id:
            raise Exception("Database failed to create new question.")
            
        return {"new_question_id": new_question_id}
    
    except Exception as e:
        logger.error(f"Error generating and creating question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate question.")


@router.post("/{objective_id}/create-question-from-draft", response_class=JSONResponse)
async def create_question_from_ai_draft(objective_id: str, question_draft: QuestionDraft):
    """
    Receives an EDUCATOR-APPROVED draft from the UI.
    Saves the new question, answers, and association to the DB.
    """
    try:
        # Pydantic has *already validated* the 'question_draft' data
        # If the data was bad, FastAPI would have already returned a 422.
        
        new_question_id = db.create_question_from_ai(
            question_data=question_draft.model_dump(),
            objective_id=objective_id
        )
        
        if not new_question_id:
            raise Exception("Database failed to create new question.")
            
        return {"new_question_id": new_question_id}

    # --- === THIS IS THE NEW LOGGING CODE === ---
    # We are overriding the default 422 error to add logging
    except ValidationError as e:
        logger.error(f"--- VALIDATION ERROR (422) ---")
        logger.error(f"Received bad data from client: {e.json()}")
        logger.error(f"---------------------------------")
        raise HTTPException(status_code=422, detail=e.errors())
    # --- === END OF NEW CODE === ---
    
    except Exception as e:
        logger.error(f"Error creating question from draft: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save approved question.")