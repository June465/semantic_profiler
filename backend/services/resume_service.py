# In backend/services/resume_service.py

from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional 

from backend.database import models
from backend.core import resume_parser, text_splitter, embedding_generator, vector_store

# --- 1. DEFINE THE PERMANENT UPLOAD DIRECTORY ---
UPLOAD_DIR = Path("/app/uploaded_resumes")

class ResumeServiceError(Exception):
    """Custom exception for resume service failures."""
    pass

async def process_and_store_resume(db: Session, file: UploadFile) -> models.Resume:
    """
    Saves and processes an uploaded resume file.
    """
    if not file.filename:
        raise ResumeServiceError("Uploaded file has no filename.")

    # --- 2. CREATE THE DIRECTORY IF IT DOESN'T EXIST ---
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # --- 3. DEFINE THE PERMANENT FILE PATH ---
    # We save the file here permanently so we can serve it later.
    permanent_file_path = UPLOAD_DIR / file.filename

    try:
        # --- 4. SAVE THE FILE TO THE PERMANENT PATH ---
        content = await file.read()
        with open(permanent_file_path, "wb") as buffer:
            buffer.write(content)

        # 2. Parse Resume from the new permanent path
        parsed_text = resume_parser.parse_resume_file(permanent_file_path)
        if not parsed_text:
            raise ResumeServiceError("Failed to extract text from resume.")

        # 3. Create Resume entry in database
        # We store the base filename, not the full path.
        db_resume = models.Resume(filename=file.filename, parsed_text=parsed_text)
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        # 4. Clean and Chunk Text
        cleaned_text = text_splitter.clean_text(parsed_text)
        chunks = text_splitter.split_text_into_chunks(cleaned_text)

        if not chunks:
            print(f"Warning: No chunks for resume {db_resume.id}.")
            return db_resume

        # 5. Generate Embeddings for Chunks
        embedding_model = embedding_generator.initialize_embedding_model()
        chunk_embeddings_np = embedding_generator.get_embeddings(chunks, embedding_model)

        # 6. Prepare Metadata for FAISS
        faiss_metadata = [{
            "resume_id": db_resume.id,
            "chunk_index": i,
            "chunk_text": chunk_text
        } for i, chunk_text in enumerate(chunks)]

        # 7. Add Embeddings to FAISS
        vector_store.add_embeddings_to_index(chunk_embeddings_np, faiss_metadata)
        print(f"Resume {db_resume.id} processed and stored.")

        return db_resume

    except Exception as e:
        # If anything fails, rollback the DB and try to delete the saved file.
        db.rollback()
        if os.path.exists(permanent_file_path):
            os.remove(permanent_file_path)
        raise ResumeServiceError(f"An unexpected error occurred: {e}")
    # --- 5. REMOVED THE 'finally' BLOCK THAT DELETED THE FILE ---

async def get_resume_by_id(db: Session, resume_id: int) -> Optional[models.Resume]:
    """
    Retrieves a resume by its ID from the database.
    """
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()