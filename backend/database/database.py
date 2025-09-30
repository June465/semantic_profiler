import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base # Import Base from models.py

# Load environment variables (e.g., from .env file)
from dotenv import load_dotenv
load_dotenv()

# Get the database URL from environment variables
# For Docker Compose, the hostname 'db' refers to the MySQL service
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db:3306/semantic_profiler_db")

# Create the SQLAlchemy engine
# pool_pre_ping=True helps maintain database connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

# Create a SessionLocal class to get database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to provide a database session to FastAPI routes.
    Ensures the session is closed after the request.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Creates all defined database tables based on SQLAlchemy models.
    """
    print("Attempting to create database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created or already exist.")

if __name__ == '__main__':
    # This block allows you to run this file directly to create tables
    # Useful for initial setup or migrations.
    print("--- Database Setup ---")
    create_tables()