"""
API module for the Question App.

This module contains all the API endpoints organized by functionality.
"""

from .canvas import router as canvas_router
from .chat import router as chat_router
from .debug import router as debug_router
from .objectives import router as objectives_router
from .questions import router as questions_router
from .system_prompt import router as system_prompt_router
from .vector_store import router as vector_store_router

__all__ = [
    "canvas_router",
    "questions_router",
    "chat_router",
    "system_prompt_router",
    "objectives_router",
    "vector_store_router",
    "debug_router",
]
