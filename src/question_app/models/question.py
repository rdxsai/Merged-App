"""
Pydantic models for data validation and structure.

--- THIS IS THE NEW, CORRECTED VERSION ---

These models have been updated to match the new database schema
and the data being sent by the new edit_question.html JavaScript.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

# This tells Pydantic V2 to use 'from_attributes' (the new 'orm_mode')
model_config = ConfigDict(from_attributes=True)

# This is the "shape" of a single answer in our new JavaScript
class AnswerUpdate(BaseModel):
    model_config = model_config
    
    id: str                 # <-- Correctly a string (for the UUID)
    text: str
    is_correct: bool
    feedback_text: Optional[str] = ""
    feedback_approved: bool

# This is the main model for the auto-save PUT request
# It now perfectly matches our JavaScript's 'collectFormData'
class QuestionUpdate(BaseModel):
    model_config = model_config
    
    question_text: str
    
    # It now expects 'objective_ids' as a list of strings
    objective_ids: List[str] = Field(default_factory=list)
    
    # It now expects a list of the new 'AnswerUpdate' models
    answers: List[AnswerUpdate]


# --- Models for creating NEW questions ---

class NewAnswer(BaseModel):
    """Model for creating a new answer (doesn't need an ID)"""
    model_config = model_config
    
    text: str
    is_correct: bool = False

class NewQuestion(BaseModel):
    """
    Pydantic model for creating new questions.
    (Updated to match our new database)
    """
    model_config = model_config
    
    question_text: str
    objective_ids: List[str] = Field(default_factory=list)
    answers: List[NewAnswer] = []