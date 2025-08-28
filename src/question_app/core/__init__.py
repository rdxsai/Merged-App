"""
Core package for the Question App.

This package contains core application logic, configuration, and
fundamental components.
"""

from .config import config, Config
from .logging import setup_logging, get_logger
from .app import create_app, register_routers, get_templates

__all__ = [
    "config",
    "Config", 
    "setup_logging",
    "get_logger",
    "create_app",
    "register_routers",
    "get_templates"
]
