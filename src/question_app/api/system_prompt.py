"""
System Prompt API module for the Question App.

This module contains all system prompt management functionality including:
- System prompt editing endpoints
- System prompt API endpoints
- Test system prompt functionality
"""

import logging

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..utils import (
    load_system_prompt,
    save_system_prompt,
)

logger = logging.getLogger(__name__)

# Create router for system prompt endpoints
router = APIRouter(prefix="/system-prompt", tags=["system-prompt"])

# Templates setup
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def get_system_prompt_page(request: Request):
    """Get the system prompt editing page"""
    prompt = load_system_prompt()
    return templates.TemplateResponse(
        "system_prompt_edit.html", 
        {"request": request, "current_prompt": prompt}
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
            return {
                "success": True, 
                "message": "System prompt saved successfully"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to save system prompt"
            )
    except Exception as e:
        logger.error(f"Error saving system prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test", response_class=HTMLResponse)
async def test_system_prompt_page(request: Request):
    """Test page for system prompt functionality"""
    return templates.TemplateResponse(
        "test_system_prompt.html", {"request": request}
    )
