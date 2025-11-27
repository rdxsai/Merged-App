"""
Chat API module for the Question App.
(This is the corrected version that fixes initialization and student creation)
"""

from typing import Dict
from fastapi.openapi.utils import status_code_ranges
from pydantic import BaseModel
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..core import config, get_logger
from ..utils import (
    get_default_chat_system_prompt,
    get_default_welcome_message,
    load_chat_system_prompt,
    load_welcome_message,       # <-- We will use this
    save_chat_system_prompt,
    save_welcome_message,
)
from ..services.tutor.hybrid_system import HybridCrewAISocraticSystem
from ..api.vector_store import ChromaVectorStoreService


logger = get_logger(__name__)

# Create router for chat endpoints
router = APIRouter(prefix="/chat", tags=["chat"])

# Templates setup
templates = Jinja2Templates(directory="templates")

# --- === (This initialization is correct) === ---
try:
    vector_service = ChromaVectorStoreService()
    
    azure_config = {
        "api_key": config.AZURE_OPENAI_SUBSCRIPTION_KEY,
        "endpoint": config.AZURE_OPENAI_ENDPOINT,
        "deployment_name": config.AZURE_OPENAI_DEPLOYMENT_ID,
        "api_version": config.AZURE_OPENAI_API_VERSION
    }

    tutor_system = HybridCrewAISocraticSystem(
        azure_config=azure_config,
        vector_store_service=vector_service,
        db_path=config.db_path 
    )
    logger.info("Chat API: HybridCrewAISocraticSystem initialized successfully.")

except ValueError as e:
    logger.critical(f"Failed to initialize ChromaDB client: {e}")
    logger.critical("Please ensure the ChromaDB server is running. Try: 'chroma run'")
    tutor_system = None
except Exception as e:
    logger.critical(f"Failed to initialize HybridCrewAISocraticSystem: {e}", exc_info=True)
    tutor_system = None
# --- === END OF INITIALIZATION === ---


# Chat endpoints
@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat assistant page"""
    return templates.TemplateResponse("chat.html", {"request": request})


#Define a pydantic model for incoming request body
class ChatMessage(BaseModel):
    message : str
    student_id: str | None = None 

# --- Constants for our new default student ---
DEFAULT_STUDENT_ID = "default-student"
DEFAULT_STUDENT_NAME = "Default Student"
DEFAULT_TOPIC = "Web Accessibility"

@router.post("/message")
async def handle_chat_message(chat_message : ChatMessage):
    """
    Handles a single chat message via POST request.
    (This is the updated, corrected version)
    """
    
    if not tutor_system:
        logger.error("Tutor system is not initialized. ChromaDB might be offline.")
        raise HTTPException(status_code=503, detail="Tutor system is offline. Please check server logs.")

    try:
        # --- (Default student logic is correct) ---
        student_id = chat_message.student_id or DEFAULT_STUDENT_ID
        
        profile = tutor_system.get_student_profile(student_id)
        if not profile:
            logger.warning(f"Student profile '{student_id}' not found. Creating a default profile.")
            try:
                tutor_system.create_student_profile(
                    name=DEFAULT_STUDENT_NAME,
                    topic=DEFAULT_TOPIC,
                    student_id_override=student_id 
                )
                # After creating, we must load the profile again to use it
                profile = tutor_system.get_student_profile(student_id)
                if not profile: # Still not found? Something is wrong.
                    raise Exception("Failed to create or load default student profile.")
            except Exception as create_e:
                logger.error(f"Failed to create default student profile: {create_e}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to create student profile.")
        # --- (End of default student logic) ---

        
        # --- === THIS IS THE NEW FIX === ---
        # If the message is "START_SESSION", just send the welcome message.
        if chat_message.message == "START_SESSION":
            logger.info(f"Handling new conversation start for student_id: {student_id}")
            welcome_message = load_welcome_message() # Use the existing utility
            
            # We increment the session count
            if profile:
                profile.total_sessions += 1
                tutor_system.db.save_student_profile(profile)
                
            return {
                "response": welcome_message,
                "student_id": student_id,
                "session_metadata": {
                    "session_number": profile.total_sessions if profile else 1,
                    "intent_executed": "start_session",
                    "analysis": {}, "progress": {} # Send empty metadata
                }
            }
        # --- === END OF NEW FIX === ---

        
        # If the message is not "START_SESSION", proceed with the normal AI workflow
        logger.info(f"Received chat message for student_id: {student_id}")
        
        result = await tutor_system.conduct_socratic_session(
            student_id=student_id,
            student_response=chat_message.message
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500 , detail = result.get("error" , "An unknown error occured in tutoring session"))
        
        return {
            "response" : result.get("tutor_response"),
            "student_id": student_id, 
            "session_metadata" : result.get("session_metadata")
        }
    except HTTPException as e:
        logger.error(f"HTTP Exception in handle_chat_message : {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in handle_chat_message : {e}" , exc_info=True)
        raise HTTPException(
            status_code=500 , detail = f"Failed to process chat message : {str(e)}"
        )

# (The rest of your file for /system-prompt and /welcome-message is unchanged and correct)
# ...
@router.get("/system-prompt", response_class=HTMLResponse)
async def chat_system_prompt_page(request: Request):
    """Chat system prompt edit page"""
    current_prompt = load_chat_system_prompt()
    default_prompt = get_default_chat_system_prompt()

    return templates.TemplateResponse(
        "chat_system_prompt_edit.html",
        {
            "request": request,
            "current_prompt": current_prompt,
            "default_prompt": default_prompt,
        },
    )


@router.post("/system-prompt")
async def save_chat_system_prompt_endpoint(request: Request):
    """Save chat system prompt"""
    try:
        form = await request.form()
        prompt_value = form.get("prompt", "")
        prompt = prompt_value.strip() if isinstance(prompt_value, str) else ""

        if not prompt:
            raise HTTPException(status_code=400, detail="System prompt cannot be empty")

        if save_chat_system_prompt(prompt):
            logger.info("Chat system prompt saved successfully")
            return {"success": True, "message": "Chat system prompt saved successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save chat system prompt"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error saving chat system prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-prompt/default")
async def get_default_chat_system_prompt_endpoint():
    """Get default chat system prompt"""
    return {"default_prompt": get_default_chat_system_prompt()}


@router.get("/welcome-message")
async def get_chat_welcome_message():
    """Get the current chat welcome message"""
    try:
        welcome_message = load_welcome_message()
        return {"welcome_message": welcome_message}
    except Exception as e:
        logger.error(f"Error loading welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/welcome-message")
async def save_chat_welcome_message(request: Request):
    """Save chat welcome message"""
    try:
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            body = await request.json()
            message = body.get("welcome_message", "").strip()
        else:
            form = await request.form()
            message_value = form.get("welcome_message", "")
            message = message_value.strip() if isinstance(message_value, str) else ""

        if not message:
            raise HTTPException(
                status_code=400, detail="Welcome message cannot be empty"
            )

        if save_welcome_message(message):
            logger.info("Welcome message saved successfully")
            return {"success": True, "message": "Welcome message saved successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to save welcome message"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error saving welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/welcome-message/default")
async def get_default_chat_welcome_message():
    """Get default chat welcome message"""
    try:
        default_message = get_default_welcome_message()
        return {"default_welcome_message": default_message}
    except Exception as e:
        logger.error(f"Error loading default welcome message: {e}")
        raise HTTPException(status_code=500, detail=str(e))