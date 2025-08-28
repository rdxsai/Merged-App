"""
Learning objectives management API endpoints.

This module contains FastAPI endpoints for managing learning objectives,
including viewing and saving objectives.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..core import get_logger
from ..models.objective import ObjectivesUpdate
from ..utils.file_utils import load_objectives, save_objectives

# Configure logging
logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/objectives", tags=["objectives"])

# Templates
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def objectives_page(request: Request):
    """
    Learning objectives management page.
    
    Returns:
        HTMLResponse: Rendered objectives management page with current 
        objectives.
    """
    objectives = load_objectives()
    return templates.TemplateResponse(
        "objectives.html", 
        {"request": request, "objectives": objectives}
    )


@router.post("/")
async def save_objectives_endpoint(objectives_data: ObjectivesUpdate):
    """
    Save learning objectives.
    
    Args:
        objectives_data (ObjectivesUpdate): The objectives data to save.
        
    Returns:
        dict: Success response with message.
        
    Raises:
        HTTPException: If saving fails.
    """
    try:
        # Convert Pydantic models to dictionaries
        objectives_list = [
            obj.model_dump() for obj in objectives_data.objectives
        ]

        if save_objectives(objectives_list):
            logger.info(f"Saved {len(objectives_list)} learning objectives")
            return {
                "success": True,
                "message": (
                    f"Successfully saved {len(objectives_list)} "
                    f"learning objectives"
                ),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save learning objectives"
            )
    except Exception as e:
        logger.error(f"Error saving objectives: {e}")
        raise HTTPException(status_code=500, detail=str(e))
