import json
import os
import sqlite3
import uuid
import random
from datetime import datetime
import os
import sys

#Adding the src directory to the path so we can import our services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

try:
    from question_app.services.database import DatabaseManager
except ImportError:
    print("Error : Could not import Database Manager. Make sure you are running this from project root")
    sys.exit(1)

print("Starting db seeding..")

#Define paths
DB_PATH = "data/socratic_tutor.db"
OBJECTIVES_JSON = "data/learning_objectives.json"
QUESTIONS_JSON = "data/quiz_questions.json"

#Initialize the DB
db = DatabaseManager(db_path=DB_PATH)

def get_all_objective_ids():
    cursor = db.get_connection().cursor()
    cursor.execute("SELECT id FROM learning_objectives")
    return [row[0] for row in cursor.fetchall()]


#loading and inserting learning objectives from json into DB
print(f"Loading objectives from {OBJECTIVES_JSON}")
try:
    with open(OBJECTIVES_JSON , 'r') as f:
        objectives = json.load(f)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for obj_text in objectives:
            cursor.execute(
                "INSERT OR IGNORE INTO learning_objectives(id, text, created_at) VALUES (?, ?, ?)",
                (str(uuid.uuid4()), obj_text, datetime.now().isoformat()),
            )
            conn.commit()
except Exception as e:
    print(f"Error loading objectives : {e}")


#Loading and inserting Questions(with Answers)
print(f"Loading questions from {QUESTIONS_JSON}")
try:
    with open(QUESTIONS_JSON , 'r') as f:
        questions = json.load(f)
    with db.get_connection() as conn:
        cursor = conn.cursor()

        all_objective_ids = get_all_objective_ids(conn)

        for q in questions:
            q_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT OR IGNORE INTO questions (id, question_text, created_at) VALUES (?, ?, ?)",
                (q_id , q['question_text'], datetime.now().isoformat())
            )

            for a in q.get('answers' , []):
                a_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO answers 
                    (id, question_id, text, is_correct, feedback_text, feedback_approved) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (a_id,  q_id , a['text'] , a['weight'] > 0 , a.get('comments' , '') , False)
                )

            if all_objective_ids:
                num_to_assign = random.randint(1 , min(2 , len(all_objective_ids)))
                assigned_ids = random.sample(all_objective_ids , num_to_assign)

                for obj_id in assigned_ids:
                    cursor.execute(
                                                """
                        INSERT OR IGNORE INTO question_objective_associations 
                        (id, question_id, objective_id) VALUES (?, ?, ?)
                        """,
                        (str(uuid.uuid4()) , q_id , obj_id)
                    )
        
        conn.commit()
    print(f"Successfully inserted {len(questions)} questions and their answers/associations.")
except Exception as e:
    print(f"Error loading questions : {e}")

print("DB seeding complete !")

