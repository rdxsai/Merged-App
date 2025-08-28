"""
Question App - A comprehensive web application for managing Canvas LMS quiz
questions.

This package provides a FastAPI-based web application for managing Canvas LMS
quiz questions with AI-powered feedback generation and an intelligent chat
assistant using RAG (Retrieval-Augmented Generation).
"""

__version__ = "0.2.0"
__author__ = "Bryce Kayanuma <BrycePK@vt.edu>, " "Robert Fentress <learn@vt.edu>"

from .main import app

__all__ = ["app"]
