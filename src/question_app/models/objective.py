"""
Learning objective-related Pydantic models for the Canvas Quiz Manager.

This module contains all Pydantic models related to learning objectives.
"""

from typing import List
from pydantic import BaseModel


class LearningObjective(BaseModel):
    """
    Pydantic model representing a learning objective.

    Attributes:
        text (str): The learning objective text
        blooms_level (str): Bloom's taxonomy level (e.g., 'understand')
        priority (str): Priority level ('low', 'medium', 'high')
    """

    text: str
    blooms_level: str = "understand"
    priority: str = "medium"


class ObjectivesUpdate(BaseModel):
    """
    Pydantic model for updating learning objectives.

    Attributes:
        objectives (List[LearningObjective]): List of learning objectives
    """

    objectives: List[LearningObjective] = []
