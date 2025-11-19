
import json
import logging
import os
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.tutor import StudentProfile, KnowledgeLevel, SessionPhase

class DatabaseManager:
    def __init__(self, db_path: str = "socratic_tutor.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS student_profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    current_topic TEXT,
                    knowledge_level TEXT,
                    session_phase TEXT,
                    understanding_progression TEXT,
                    misconceptions TEXT,
                    strengths TEXT,
                    warning_signs TEXT,
                    consecutive_correct INTEGER DEFAULT 0,
                    engagement_level TEXT DEFAULT 'high',
                    last_solid_understanding TEXT,
                    total_sessions INTEGER DEFAULT 0,
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )
            conn.commit()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def save_student_profile(self, profile: StudentProfile) -> bool:
        try:
            profile.updated_at = datetime.now().isoformat()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO student_profiles 
                    (id, name, current_topic, knowledge_level, session_phase,
                     understanding_progression, misconceptions, strengths, warning_signs,
                     consecutive_correct, engagement_level, last_solid_understanding,
                     total_sessions, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile.id,
                        profile.name,
                        profile.current_topic,
                        profile.knowledge_level.value,
                        profile.session_phase.value,
                        json.dumps(profile.understanding_progression),
                        json.dumps(profile.misconceptions),
                        json.dumps(profile.strengths),
                        json.dumps(profile.warning_signs),
                        profile.consecutive_correct,
                        profile.engagement_level,
                        profile.last_solid_understanding,
                        profile.total_sessions,
                        profile.created_at,
                        profile.updated_at,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving student profile: {e}")
            return False

    def load_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM student_profiles WHERE id = ?", (student_id,)
                )
                row = cursor.fetchone()

                if row:
                    return StudentProfile(
                        id=row[0],
                        name=row[1],
                        current_topic=row[2],
                        knowledge_level=KnowledgeLevel(row[3]),
                        session_phase=SessionPhase(row[4]),
                        understanding_progression=json.loads(row[5] or "[]"),
                        misconceptions=json.loads(row[6] or "[]"),
                        strengths=json.loads(row[7] or "[]"),
                        warning_signs=json.loads(row[8] or "[]"),
                        consecutive_correct=row[9],
                        engagement_level=row[10],
                        last_solid_understanding=row[11],
                        total_sessions=row[12],
                        created_at=row[13],
                        updated_at=row[14],
                    )
                return None
        except Exception as e:
            logger.error(f"Error loading student profile: {e}")
            return None

    def list_all_students(self) -> List[Dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, name, current_topic, knowledge_level, session_phase, 
                           total_sessions, updated_at 
                    FROM student_profiles 
                    ORDER BY updated_at DESC
                """
                )

                students = []
                for row in cursor.fetchall():
                    students.append(
                        {
                            "id": row[0],
                            "name": row[1],
                            "topic": row[2],
                            "knowledge_level": row[3],
                            "session_phase": row[4],
                            "total_sessions": row[5],
                            "last_updated": row[6],
                        }
                    )
                return students
        except Exception as e:
            logger.error(f"Error listing students: {e}")
            return []