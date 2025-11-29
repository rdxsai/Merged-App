"""
--- OBJECTIVE SEEDER ---
This is the NEW "smart" seeder.

Run this script FIRST.

It reads your 'objectives.md' file, parses the Bloom's verbs
(e.g., **Explain**), and populates the 'learning_objective' table
with the full, rich data.
"""

import sqlite3
import re
import uuid
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
    print("Run as: poetry run python scripts/seed_objectives.py")
    sys.exit(1)

# --- CONFIGURATION ---
# These paths are relative to the project root
DB_PATH = os.path.join("data", "socratic_tutor.db")
OBJECTIVES_DOC = "objectives.md" # The .md file in your project root

# (The rest of the file is the same as I sent before)
BLOOM_MAP = {
    "identify": "remember", "list": "remember", "describe": "remember",
    "summarize": "understand", "explain": "understand", "differentiate": "understand",
    "outline": "understand",
    "compare": "analyze", "analyze": "analyze", "distinguish": "analyze",
    "map": "analyze", "interpret": "analyze", "categorize": "analyze",
    "assess": "evaluate", "evaluate": "evaluate", "justify": "evaluate",
    "recommend": "evaluate", "verify": "evaluate",
    "propose": "create", "construct": "create", "develop": "create",
    "establish": "create", "formulate": "create", "collaborate": "create",
    "integrate": "create",
    "apply": "apply", "implement": "apply", "demonstrate": "apply",
    "conduct": "apply", "use": "apply", "perform": "apply",
}

def get_blooms_level(verb: str) -> str:
    """Finds the matching Bloom's level, defaulting to 'understand'."""
    return BLOOM_MAP.get(verb.lower(), "understand")

def seed_database():
    print(f"--- Starting Objective Seeder for '{DB_PATH}' ---")
    
    # This will create the DB file and all tables if they don't exist
    try:
        db = DatabaseManager(db_path=DB_PATH)
        print("DatabaseManager initialized, tables ensured.")
    except Exception as e:
        print(f"Failed to initialize DatabaseManager: {e}")
        return

    objective_regex = re.compile(r"^\d+\.\s+\*\*(.*?)\*\*(.*)")
    objectives_found = []
    
    try:
        with open(OBJECTIVES_DOC, 'r', encoding='utf-8') as f:
            for line in f:
                match = objective_regex.match(line.strip())
                if match:
                    verb = match.group(1).strip().split()[0].lower().rstrip(',')
                    text = f"{match.group(1).strip()} {match.group(2).strip()}"
                    objective = {
                        "text": text,
                        "blooms_level": get_blooms_level(verb),
                        "priority": "medium",
                        "id": str(uuid.uuid4()),
                        "created_at": datetime.now().isoformat()
                    }
                    objectives_found.append(objective)
                    
    except FileNotFoundError:
        print(f"ERROR: '{OBJECTIVES_DOC}' not found in the root folder.")
        print("Please create it and paste the objectives into it.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Found {len(objectives_found)} objectives in '{OBJECTIVES_DOC}'.")
    if not objectives_found:
        print("No objectives found. Exiting.")
        return

    try:
        with db.get_connection(use_row_factory=False) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM learning_objective;")
            print("Cleared old objectives from database.")

            for obj in objectives_found:
                cursor.execute(
                    """
                    INSERT INTO learning_objective (id, text, created_at, blooms_level, priority)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (obj['id'], obj['text'], obj['created_at'], obj['blooms_level'], obj['priority'])
                )
            
            conn.commit()
        
        print(f"Successfully inserted {len(objectives_found)} new objectives.")
        print("--- Objective Seeding Complete! ---")
        
    except Exception as e:
        print(f"\nDATABASE ERROR: {e}")

if __name__ == "__main__":
    seed_database()