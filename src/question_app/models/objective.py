"""
Pydantic Models for Learning Objectives
"""

from pydantic import BaseModel
from typing import List, Optional

# --- Base Model ---
# This defines the common fields that are always required.
class ObjectiveBase(BaseModel):
    text: str
    blooms_level: str = 'understand'
    priority: str = 'medium'

# --- Create Model ---
# This is the data we expect from the UI when *creating* a new objective.
# The JavaScript `addNewObjective` function sends JSON that matches this.
class ObjectiveCreate(BaseModel):
    text: str # On creation, we only require text.

# --- Update Model ---
# This is the data we expect from the UI when *updating* (auto-saving).
# The JavaScript `autoSave` function sends JSON that matches this.
class ObjectiveUpdate(ObjectiveBase):
    pass # It's the same as the base model

# --- Database & Response Model ---
# This is the full data model, including fields the database adds.
# This is what we send *back* to the UI.
class ObjectiveInDB(ObjectiveBase):
    id: str
    created_at: str
    question_count: int

    class Config:
        # This allows the model to be created from database rows
        from_attributes = True

# --- Model for your old JSON file (Legacy) ---
# Your old UI was designed to save *all* objectives at once.
# Your OLD `objectives.py` API endpoint used this.
# We are no longer using this model, but this is what it would look like.
class ObjectivesFile(BaseModel):
    objectives: List[ObjectiveBase]

class AnswerDraft(BaseModel):
    text:str
    is_correct : bool

class QuestionDraft(BaseModel):
    question_text : str
    answers: List[AnswerDraft]