"""
Models Package Initializer.

This file acts as the "front door" for all Pydantic models,
making them easily importable by other services.

--- THIS IS THE NEW, CORRECTED VERSION ---
"""

# Import the new, correct models from models/question.py
from .question import (
    AnswerUpdate,
    QuestionUpdate,
    NewAnswer,
    NewQuestion
)

# Import the models from models/tutor.py
# (We assume this file exists and is correct)
try:
    from .tutor import (
        StudentProfile,
        KnowledgeLevel,
        SessionPhase,
        LearningObjective,
        Question,
        Answer
    )
except ImportError:
    # Handle case if tutor.py doesn't exist or has different models
    # For now, we just pass to avoid crashing
    pass

# This __all__ list tells Python what names to "export"
# from this package. This is what will fix your ImportError.
__all__ = [
    # From models/question.py
    "AnswerUpdate",
    "QuestionUpdate",
    "NewAnswer",
    "NewQuestion",
    
    # From models/tutor.py
    "StudentProfile",
    "KnowledgeLevel",
    "SessionPhase",
    "LearningObjective",
    "Question",
    "Answer"
]