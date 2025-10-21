"""
Chat API module for the Question App.

This module contains all RAG-based chat functionality including:
- Chat interface endpoints
- Vector store operations
- Embedding generation
- Semantic search
- Chat system prompt management
- Welcome message management
"""

from typing import Dict
from fastapi.openapi.utils import status_code_ranges
from pydantic import BaseModel
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from docs import conf

from ..core import config, get_logger
from ..utils import (
    get_default_chat_system_prompt,
    get_default_welcome_message,
    load_chat_system_prompt,
    load_welcome_message,
    save_chat_system_prompt,
    save_welcome_message,
)
from .vector_store import search_vector_store
from ..services.tutor.hybrid_system import HybridCrewAISocraticSystem
from ..api.vector_store import ChromaVectorStoreService
from question_app.api import vector_store

logger = get_logger(__name__)

# Create router for chat endpoints
router = APIRouter(prefix="/chat", tags=["chat"])

# Templates setup
templates = Jinja2Templates(directory="templates")

# Chat endpoints
@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat assistant page"""
    return templates.TemplateResponse("chat.html", {"request": request})


#Define a pydantic model for incoming request body
class ChatMessage(BaseModel):
    message : str
    student_id : str

@router.post("/message")
async def handle_chat_message(chat_message : ChatMessage):
    logger.info(f"Received chat message for student_id: {chat_message.student_id}")
    try:
        vector_service = ChromaVectorStoreService() #creating the tool that will search the vector store
        tutor_system = HybridCrewAISocraticSystem(
            azure_config={
                "api_key": config.AZURE_OPENAI_SUBSCRIPTION_KEY,
                "endpoint" : config.AZURE_OPENAI_ENDPOINT,
                "deployment_name": config.AZURE_OPENAI_DEPLOYMENT_ID,
                "api_version": config.AZURE_OPENAI_API_VERSION
            },
            vector_store_service=vector_service,
            db_path="socratic_tutor.db"
        )

        result = await tutor_system.conduct_socratic_session(
            student_id=chat_message.student_id,
            student_response=chat_message.message
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500 , detail = result.get("error" , "An unknown error occured in tutoring session"))
        return {
            "response" : result.get("tutor_response"),
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

# Chat system prompt management endpoints
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


# Welcome message management endpoints
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
        # Check if it's JSON or form data
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
