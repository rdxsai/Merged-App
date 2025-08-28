"""
Core package for the Question App.

This package contains core application logic, configuration, and
fundamental components.
"""

from .app import create_app, get_templates, register_routers
from .config import Config, config
from .logging import get_logger, setup_logging

__all__ = [
    "config",
    "Config",
    "setup_logging",
    "get_logger",
    "create_app",
    "register_routers",
    "get_templates",
]
