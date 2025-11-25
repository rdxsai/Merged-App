"""
Database Manager
Handles all SQLite database operations for the Socratic Tutor.
Manages schema and CRUD operations for all data models.
"""
import sqlite3
import json
import logging 
import uuid 
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

# --- Corrected Application Imports ---
from ..models import QuestionUpdate
from ..models.tutor import (
    StudentProfile, KnowledgeLevel, SessionPhase,
    LearningObjective, Question, Answer
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    # --- FIX 1: Path is relative to project root ---
    def __init__(self, db_path: str = "data/socratic_tutor.db"):
        self.db_path = db_path
        self._init_database() 

    def _init_database(self):
        """
        Initializes all 5 tables in the database.
        """
        # --- FIX: Added use_row_factory=False ---
        with self.get_connection(use_row_factory=False) as conn: 
            cursor = conn.cursor()
            
            # (Your table creation code is correct)
            # 1. Student Profiles Table
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
            # 2. Learning Objective Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_objective (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL UNIQUE,
                    created_at TEXT
                )
            """
            )
            # 3. Question Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS question (
                    id TEXT PRIMARY KEY,
                    question_text TEXT NOT NULL,
                    created_at TEXT
                )
            """
            )
            # 4. Answer Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS answer (
                    id TEXT PRIMARY KEY,
                    question_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL DEFAULT 0,
                    feedback_text TEXT,
                    feedback_approved BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (question_id) REFERENCES question (id) ON DELETE CASCADE
                )
            """
            )
            # 5. Association Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS question_objective_association (
                    id TEXT PRIMARY KEY,
                    question_id TEXT NOT NULL,
                    objective_id TEXT NOT NULL,
                    FOREIGN KEY (question_id) REFERENCES question (id) ON DELETE CASCADE,
                    FOREIGN KEY (objective_id) REFERENCES learning_objective (id) ON DELETE CASCADE,
                    UNIQUE(question_id, objective_id)
                )
            """
            )
            conn.commit()

    # --- FIX 2: Updated get_connection to use row_factory ---
    @contextmanager
    def get_connection(self, use_row_factory: bool = True):
        """
        Provides a database connection.
        Uses sqlite3.Row factory by default for dict-like access.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            if use_row_factory:
                conn.row_factory = sqlite3.Row 
            yield conn
        finally:
            conn.close()

    def get_answers_for_questions(self, question_id:str) -> List[Dict]:
        """ Gets all answers for a given question ID. """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM answer WHERE question_id = ? ORDER BY id",
                (question_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def list_all_objectives(self) -> List[Dict]:
        """ Gets all objectives for dropdowns. """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
               "SELECT id, text FROM learning_objective ORDER BY text" 
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def load_question_details(self,question_id:str) -> Optional[Dict[str , Any]]:
        """
        Loads a single question, its answers, and its associated
        objective IDs. Returns a dictionary.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM question WHERE id = ?" , (question_id,))
                # --- FIX 3: Use fetchone() for a single item, not fetchall() ---
                question_row = cursor.fetchone() 
                if not question_row:
                    return None
                
                question = dict(question_row) 
                question['answers'] = self.get_answers_for_questions(question_id)

                cursor.execute(
                    "SELECT objective_id FROM question_objective_association WHERE question_id = ?",
                    (question_id,)
                )
                objective_rows = cursor.fetchall()
                question['objective_ids'] = [row['objective_id'] for row in objective_rows]
                return question
        except Exception as e:
            logger.error(f"Error loading question details for {question_id} : {e}" , exc_info=True)
            return None
        
    
    def update_question_and_answers(self, question_id:str , data:QuestionUpdate) -> bool:
        """ Updates a question and its answers from the Pydantic model. """
        try:
            # --- FIX: Added use_row_factory=False ---
            with self.get_connection(use_row_factory=False) as conn: 
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE question SET question_text = ? WHERE id = ?",
                    (data.question_text , question_id)
                )

                for answer in data.answers:
                    # --- FIX 4: Added 'answer.feedback_approved' to tuple ---
                    cursor.execute(
                        """
                        UPDATE answer 
                        SET text = ?, is_correct = ?, feedback_text = ?, feedback_approved = ?
                        WHERE id = ? AND question_id = ?
                        """,
                        (
                            answer.text,
                            answer.is_correct,
                            answer.feedback_text,
                            answer.feedback_approved, # This was missing
                            answer.id,
                            question_id
                        )
                    )
                
                cursor.execute(
                    "DELETE FROM question_objective_association WHERE question_id = ?",
                    (question_id,)
                )
                if data.objective_ids:
                    for obj_id in data.objective_ids:
                        if obj_id:
                            cursor.execute(
                                "INSERT INTO question_objective_association (id, question_id, objective_id) VALUES (?, ?, ?)",
                                (str(uuid.uuid4()) , question_id , obj_id)
                            )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating question {question_id} : {e}" , exc_info=True)
            return False
    
    def update_answer_feedback(self, answer_id:str , feedback_text:str) -> bool:
        """ (Req 4) Updates ONLY the feedback for a single answer. """
        try:
            with self.get_connection(use_row_factory=False) as conn: 
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE answer SET feedback_text = ? WHERE id = ?",
                    (feedback_text , answer_id)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating feedback for answer {answer_id}: {e}" , exc_info =True)
            return False

    def delete_question(self, question_id:str) -> bool:
        """ Deletes a question. ON DELETE CASCADE will handle answers/associations. """
        try:
            with self.get_connection(use_row_factory=False) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM question WHERE id = ?" , (question_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting question {question_id} : {e}" , exc_info=True)
            return False

    # --- Student Profile Methods ---
    def load_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM student_profiles WHERE id = ?", (student_id,)
                )
                row = cursor.fetchone()
                if row:
                    # This is a bit different from your version, but safer
                    return StudentProfile(
                        id=row["id"],
                        name=row["name"],
                        current_topic=row["current_topic"],
                        knowledge_level=KnowledgeLevel(row["knowledge_level"]),
                        session_phase=SessionPhase(row["session_phase"]),
                        understanding_progression=json.loads(row["understanding_progression"] or "[]"),
                        misconceptions=json.loads(row["misconceptions"] or "[]"),
                        strengths=json.loads(row["strengths"] or "[]"),
                        warning_signs=json.loads(row["warning_signs"] or "[]"),
                        consecutive_correct=row["consecutive_correct"],
                        engagement_level=row["engagement_level"],
                        last_solid_understanding=row["last_solid_understanding"],
                        total_sessions=row["total_sessions"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                return None
        except Exception as e:
            logger.error(f"Error loading student profile {student_id}: {e}", exc_info=True)
            return None
    
    def save_student_profile(self, profile: StudentProfile) -> bool:
        try:
            profile.updated_at = datetime.now().isoformat()
            with self.get_connection(use_row_factory=False) as conn:
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
            logger.error(f"Error saving student profile: {e}", exc_info=True)
            return False

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
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing students: {e}", exc_info=True)
            return []
    
    # --- === THIS IS THE NEW METHOD YOU NEED === ---
    
    def list_all_questions(self) -> List[Dict]:
        """
        Fetches all questions from the database for the home page.
        
        This query joins with the association table to get a *count*
        of how many objectives are linked to each question.
        """
        logger.info("Fetching all questions from database for home page...")
        try:
            with self.get_connection() as conn: # This will use the row_factory
                cursor = conn.cursor()
                query = """
                    SELECT
                        q.id,
                        q.question_text,
                        q.created_at,
                        COUNT(qoa.objective_id) AS objective_count
                    FROM
                        question q
                    LEFT JOIN
                        question_objective_association qoa ON q.id = qoa.question_id
                    GROUP BY
                        q.id, q.question_text, q.created_at
                    ORDER BY
                        q.created_at DESC;
                """
                cursor.execute(query)
                questions = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Found {len(questions)} questions.")
                return questions
        except Exception as e:
            logger.error(f"Error listing all questions: {e}", exc_info=True)
            return []