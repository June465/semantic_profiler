# In backend/services/resume_service.py

from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional 

from backend.database import models
from backend.core import resume_parser, text_splitter, embedding_generator, vector_store

UPLOAD_DIR = Path("/app/uploaded_resumes")

class ResumeServiceError(Exception):
    pass

async def process_and_store_resume(db: Session, file: UploadFile) -> models.Resume:
    if not file.filename:
        raise ResumeServiceError("Uploaded file has no filename.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    permanent_file_path = UPLOAD_DIR / file.filename

    try:
        content = await file.read()
        with open(permanent_file_path, "wb") as buffer:
            buffer.write(content)

        parsed_text = resume_parser.parse_resume_file(permanent_file_path)
        if not parsed_text:
            raise ResumeServiceError("Failed to extract text from resume.")

        db_resume = models.Resume(filename=file.filename, parsed_text=parsed_text)
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        cleaned_text = text_splitter.clean_text(parsed_text)
        chunks = text_splitter.split_text_into_chunks(cleaned_text)

        if not chunks:
            print(f"Warning: No chunks for resume {db_resume.id}.")
            return db_resume

        embedding_model = embedding_generator.initialize_embedding_model()
        chunk_embeddings_np = embedding_generator.get_embeddings(chunks, embedding_model)

        faiss_metadata = [{
            "resume_id": db_resume.id,
            "chunk_index": i,
            "chunk_text": chunk_text
        } for i, chunk_text in enumerate(chunks)]

        vector_store.add_embeddings_to_index(chunk_embeddings_np, faiss_metadata)
        print(f"Resume {db_resume.id} processed and stored.")

        return db_resume

    except Exception as e:
        db.rollback()
        if os.path.exists(permanent_file_path):
            os.remove(permanent_file_path)
        raise ResumeServiceError(f"An unexpected error occurred: {e}")

async def get_resume_by_id(db: Session, resume_id: int) -> Optional[models.Resume]:
    """
    Retrieves a resume by its ID from the database.
    """
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()