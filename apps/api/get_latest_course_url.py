
import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add src to path if needed (simplified approach here)
DB_URL = "postgresql://learnhouse:learnhouse@localhost:5432/learnhouse"

def get_latest_course():
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            # Order by id descending 
            result = conn.execute(text("SELECT course_uuid FROM course ORDER BY id DESC LIMIT 1"))
            row = result.fetchone()
            if row:
                print(f"Latest Course UUID: {row[0]}")
                print(f"URL: http://localhost:3000/course/{row[0]}")
            else:
                print("No courses found.")
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    get_latest_course()
