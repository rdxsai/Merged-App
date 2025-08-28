"""
FastAPI application setup for the Question App.

This module centralizes FastAPI application creation, middleware setup,
and router registration.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import config
from .logging import setup_logging

# Set up logging
logger = setup_logging()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    logger.info("Creating FastAPI application")

    # Create FastAPI app
    app = FastAPI(title=config.APP_TITLE)

    # Mount static files and templates
    app.mount("/static", StaticFiles(directory="static"), name="static")
    templates = Jinja2Templates(directory="templates")

    # Store templates in app state for access in routes
    app.state.templates = templates

    logger.info("FastAPI application created successfully")

    return app


def register_routers(app: FastAPI) -> None:
    """
    Register all API routers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    logger.info("Registering API routers")

    # Import API routers
    from ..api import (
        canvas_router,
        chat_router,
        debug_router,
        objectives_router,
        questions_router,
        system_prompt_router,
        vector_store_router,
    )

    # Include API routers
    app.include_router(canvas_router)
    app.include_router(questions_router)
    app.include_router(chat_router)
    app.include_router(vector_store_router)
    app.include_router(system_prompt_router)
    app.include_router(objectives_router)
    app.include_router(debug_router)

    logger.info("API routers registered successfully")


def get_templates(app: FastAPI) -> Jinja2Templates:
    """
    Get the Jinja2Templates instance from the app state.

    Args:
        app: FastAPI application instance

    Returns:
        Jinja2Templates instance
    """
    return app.state.templates
