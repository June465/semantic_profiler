import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base 
from dotenv import load_dotenv
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@db:3306/semantic_profiler_db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():

    print("Attempting to create database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created or already exist.")

if __name__ == '__main__':
    print("--- Database Setup ---")
    create_tables()