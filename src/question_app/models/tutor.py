# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

import json
import logging
import os
import sqlite3database
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

class KnowledgeLevel(Enum):
    RECALL = "recall"
    UNDERSTANDING = "understanding"
    APPLICATION = "application"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"


class SessionPhase(Enum):
    OPENING = "opening"
    DEVELOPMENT = "development"
    CONSOLIDATION = "consolidation"


@dataclass
class StudentProfile:
    id: str
    name: str
    current_topic: str
    knowledge_level: KnowledgeLevel
    session_phase: SessionPhase
    understanding_progression: List[str] = field(default_factory=list)
    misconceptions: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    warning_signs: List[str] = field(default_factory=list)
    consecutive_correct: int = 0
    engagement_level: str = "high"
    last_solid_understanding: str = ""
    total_sessions: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class LearningObjective:
    "Represents a Single learning objective"
    id : str
    text : str
    created_at : str
    question_count : int = 0 

@dataclass
class Answer:
    """Represents an Answer"""
    id : str
    question_id : str
    text:str
    is_correct : bool
    feedback_text : Optional[str] = None
    feedback_approval : bool = False

@dataclass
class Question:
    id:str
    question_text : str
    created_at : str
    answers : List[Answer] = field(default_factory=list)
    objective_ids : List[str] = field(default_factory=list)
    




