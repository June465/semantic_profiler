from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
import json
from typing import List, Dict, Tuple, Optional 

from backend.database import models
from backend.core import resume_parser, text_splitter, embedding_generator, vector_store

class ResumeServiceError(Exception):
    """Custom exception for resume service failures."""
    pass

async def process_and_store_resume(db: Session, file: UploadFile) -> models.Resume:
    """
    Processes an uploaded resume file, extracts text, generates embeddings,
    stores resume metadata in the database, and adds embeddings to FAISS.

    Args:
        db (Session): SQLAlchemy database session.
        file (UploadFile): The uploaded resume file.

    Returns:
        models.Resume: The newly created Resume database object.

    Raises:
        ResumeServiceError: If any step in processing or storing fails.
    """
    if not file.filename:
        raise ResumeServiceError("Uploaded file has no filename.")

    # 1. Temporarily save the file to process it
    # For production, consider saving to object storage (S3, GCS)
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            content = await file.read() # Read file content asynchronously
            buffer.write(content)

        # 2. Parse Resume
        parsed_text = resume_parser.parse_resume_file(temp_file_path)
        if not parsed_text:
            raise ResumeServiceError("Failed to extract text from resume.")

        # 3. Create Resume entry in database
        db_resume = models.Resume(filename=file.filename, parsed_text=parsed_text)
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume) # Get the generated ID from the DB

        # 4. Clean and Chunk Text
        cleaned_text = text_splitter.clean_text(parsed_text)
        chunks = text_splitter.split_text_into_chunks(cleaned_text)

        if not chunks:
            print(f"Warning: No valid chunks generated for resume {db_resume.id}. It won't be searchable.")
            # Still return the resume, but it won't be in FAISS
            return db_resume

        # 5. Generate Embeddings for Chunks
        embedding_model = embedding_generator.initialize_embedding_model() # Gets singleton
        chunk_embeddings_np = embedding_generator.get_embeddings(chunks, embedding_model)

        # 6. Prepare Metadata for FAISS Indexing
        # Each metadata entry needs to link back to the resume and contain the chunk text
        # The FAISS index internal ID will be its position in vector_store._metadata_mapping
        faiss_metadata = []
        for i, chunk_text in enumerate(chunks):
            faiss_metadata.append({
                "resume_id": db_resume.id,
                "chunk_index": i,
                "chunk_text": chunk_text
            })

        # 7. Add Embeddings to FAISS Index (this also saves to disk automatically)
        vector_store.add_embeddings_to_index(chunk_embeddings_np, faiss_metadata)
        print(f"Resume {db_resume.id} processed, stored in DB, and embeddings added to FAISS.")

        return db_resume

    except resume_parser.ResumeParsingError as e:
        raise ResumeServiceError(f"Resume parsing failed: {e}")
    except embedding_generator.LLMEvaluationError as e: # Catching specific error for model init failure
        raise ResumeServiceError(f"Embedding model error: {e}")
    except vector_store.VectorStoreError as e:
        raise ResumeServiceError(f"Vector store (FAISS) error: {e}")
    except Exception as e:
        # Rollback in case of any unexpected error during processing
        db.rollback()
        raise ResumeServiceError(f"An unexpected error occurred during resume processing: {e}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path) # Clean up temporary file

async def get_resume_by_id(db: Session, resume_id: int) -> Optional[models.Resume]:
    """
    Retrieves a resume by its ID from the database.
    """
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()