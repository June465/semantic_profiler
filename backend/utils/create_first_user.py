import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.database import SessionLocal
from backend.database.models import User
from backend.core.security import get_password_hash

load_dotenv()

def create_first_user():
    db = SessionLocal()
    try:
        username = "admin"
        password = "changeme" 

        if db.query(User).filter(User.username == username).first():
            print(f"User '{username}' already exists. Skipping creation.")
            return

        hashed_password = get_password_hash(password)
        db_user = User(username=username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        print(f"Successfully created user '{username}'.")
        print("You can now log in with this user.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Running script to create the first user...")
    create_first_user()