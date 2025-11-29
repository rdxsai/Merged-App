"""
--- QUESTION SEEDER ---
This is your original seeder script, but modified.

Run this script SECOND.
"""

import json
import os
import sqlite3
import uuid
import random
from datetime import datetime
import os
import sys

# --- === THIS IS THE FIX === ---
# This line adds the project's root folder ("questionapp/") to the path,
# so the `from src.question_app...` import will work.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
# --- === END OF FIX === ---

try:
    from src.question_app.services.database import DatabaseManager
except ImportError as e:
    print(f"ImportError: {e}")
    print("Failed to import DatabaseManager. Make sure you are in the 'questionapp' root folder.")
    print("Run as: poetry run python scripts/seed_questions_and_aswers.py")
    sys.exit(1)

print("--- Starting Question Seeder (No Associations) ---")

# Define paths (relative to root)
DB_PATH = "data/socratic_tutor.db"
QUESTIONS_JSON = "data/quiz_questions.json"

# Initialize the DB
db = DatabaseManager(db_path=DB_PATH)
print(f"Database initialized at {DB_PATH}")

# (The rest of your file is unchanged and correct)
# Loading and inserting Questions (with Answers)
print(f"Loading questions from {QUESTIONS_JSON}...")
try:
    with open(QUESTIONS_JSON, 'r') as f:
        questions = json.load(f)
    
    with db.get_connection(use_row_factory=False) as conn:
        cursor = conn.cursor()

        # Clear old question-related data
        cursor.execute("DELETE FROM question;")
        cursor.execute("DELETE FROM answer;")
        cursor.execute("DELETE FROM question_objective_association;")
        print("Cleared old questions, answers, and associations.")

        for q in questions:
            q_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO question (id, question_text, created_at) VALUES (?, ?, ?)",
                (q_id, q['question_text'], datetime.now().isoformat())
            )

            for a in q.get('answers', []):
                a_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT INTO answer
                    (id, question_id, text, is_correct, feedback_text, feedback_approved) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (a_id, q_id, a['text'], a['weight'] > 0, a.get('comments', ''), False)
                )
        
        conn.commit()
    print(f"Successfully inserted {len(questions)} questions and their answers.")
except FileNotFoundError:
    print(f"ERROR: {QUESTIONS_JSON} not found.")
except Exception as e:
    print(f"Error loading questions: {e}")

print("--- Question Seeding Complete! ---")