"""
API module for the Question App.

This module contains all the API endpoints organized by functionality.
"""

from .canvas import router as canvas_router

__all__ = ["canvas_router"]
