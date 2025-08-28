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

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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


@router.post("/message")
async def chat_message(request: Request):
    """Process chat message with RAG using vector store"""
    try:
        # Parse request body
        body = await request.json()
        user_message = body.get("message", "").strip()
        max_chunks = body.get("max_chunks", 3)

        # Validate max_chunks
        if not isinstance(max_chunks, int) or max_chunks < 1 or max_chunks > 10:
            max_chunks = 3

        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        logger.info(f"=== Chat Message Processing Started ===")
        logger.info(f"User message: {user_message}")
        logger.info(f"Max chunks requested: {max_chunks}")

        # Search vector store for relevant chunks
        logger.info("Searching vector store for relevant context...")
        retrieved_chunks = await search_vector_store(user_message, n_results=max_chunks)
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks")

        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(f"Context {i+1}:\n{chunk['content']}")

        context = (
            "\n\n".join(context_parts)
            if context_parts
            else "No relevant context found."
        )

        # Load custom chat system prompt and inject context
        chat_system_prompt_template = load_chat_system_prompt()
        system_prompt = chat_system_prompt_template.format(context=context)

        # Prepare messages for Azure OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Call Azure OpenAI for chat completion
        logger.info("Calling Azure OpenAI for chat completion...")

        url = (
            f"{config.AZURE_OPENAI_ENDPOINT}/us-east/deployments/"
            f"{config.AZURE_OPENAI_DEPLOYMENT_ID}/chat/completions"
            f"?api-version={config.AZURE_OPENAI_API_VERSION}"
        )

        headers: Dict[str, str] = {
            "Ocp-Apim-Subscription-Key": str(
                config.AZURE_OPENAI_SUBSCRIPTION_KEY or ""
            ),
            "Content-Type": "application/json",
        }

        payload = {
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Azure OpenAI API error: {error_text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"AI service error: {error_text}",
                )

            result = response.json()

            if "choices" not in result or not result["choices"]:
                raise HTTPException(
                    status_code=500, detail="Invalid response from AI service"
                )

            ai_response = result["choices"][0]["message"]["content"]

            # Log token usage if available
            if "usage" in result:
                usage = result["usage"]
                logger.info(
                    f"Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                    f"Completion: {usage.get('completion_tokens', 0)}, "
                    f"Total: {usage.get('total_tokens', 0)}"
                )

        logger.info("Chat message processed successfully")

        return {
            "response": ai_response,
            "retrieved_chunks": retrieved_chunks,
            "context_used": len(context_parts) > 0,
        }

    except HTTPException as e:
        logger.error(f"HTTP Exception in chat_message: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in chat_message: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process chat message: {str(e)}"
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
