"""
System Prompt API module for the Question App.

This module contains all system prompt management functionality including:
- System prompt editing endpoints
- System prompt API endpoints
- Test system prompt functionality
"""

from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from ..core import get_logger
from ..utils import (
    load_system_prompt,
    save_system_prompt,
    load_feedback_prompt_from_json,
    save_feedback_prompt_to_json
)

logger = get_logger(__name__)

# Create router for system prompt endpoints
router = APIRouter(prefix="/system-prompt", tags=["system-prompt"])

# Templates setup
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_system_prompt_page(request: Request):
    """Get the system prompt editing page"""
    correct_prompt = load_feedback_prompt_from_json("feedback_correct")
    incorrect_prompt = load_feedback_prompt_from_json("feedback_incorrect")
    return templates.TemplateResponse(
        "system_prompt_edit.html", {"request": request, "current_prompt_correct": correct_prompt, "current_prompt_incorrect" : incorrect_prompt}
    )


@router.get("/api")
async def get_system_prompt_api():
    """Get the current system prompt as JSON (for API calls)"""
    prompt = load_system_prompt()
    return {"prompt": prompt}


@router.post("/")
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


@router.get("/test", response_class=HTMLResponse)
async def test_system_prompt_page(request: Request):
    """Test page for system prompt functionality"""
    return templates.TemplateResponse("test_system_prompt.html", {"request": request})


@router.get("/feedback/correct")
async def get_feedback_prompt_correct():
    """Get the current feedback prompt for correct answers"""
    try:
        prompt = load_feedback_prompt_from_json("feedback_correct")
        return {"prompt": prompt, "success": True}
    except Exception as e:
        logger.error(f"Error getting correct feedback prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/correct")
async def save_feedback_prompt_correct_endpoint(prompt: str = Form(...)):
    """Save the feedback prompt for correct answers"""
    try:
        if save_feedback_prompt_to_json("feedback_correct", prompt):
            logger.info("Correct feedback prompt updated")
            return {"success": True, "message": "Correct feedback prompt saved successfully"}
        raise HTTPException(status_code=500, detail="Failed to save correct feedback prompt")
    except Exception as e:
        logger.error(f"Error saving correct feedback prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/incorrect")
async def get_feedback_prompt_incorrect():
    """Get the current feedback prompt for incorrect answers"""
    try:
        prompt = load_feedback_prompt_from_json("feedback_incorrect")
        return {"prompt": prompt, "success": True}
    except Exception as e:
        logger.error(f"Error getting incorrect feedback prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/incorrect")
async def save_feedback_prompt_incorrect_endpoint(prompt: str = Form(...)):
    """Save the feedback prompt for incorrect answers"""
    try:
        if save_feedback_prompt_to_json("feedback_incorrect",prompt):
            logger.info("Incorrect feedback prompt updated")
            return {"success": True, "message": "Incorrect feedback prompt saved successfully"}
        raise HTTPException(status_code=500, detail="Failed to save incorrect feedback prompt")
    except Exception as e:
        logger.error(f"Error saving incorrect feedback prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))
