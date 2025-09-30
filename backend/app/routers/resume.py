from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.database import get_db
from backend.services import resume_service
from backend.schemas import resume as resume_schemas # Use alias to avoid name conflict
from backend.database import models

# Create an API router for resume-related endpoints
router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)

@router.post("/", response_model=resume_schemas.ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="The resume file to upload (PDF or DOCX)."),
    db: Session = Depends(get_db)
):
    """
    Uploads a resume file, parses its content, stores it in the database,
    and indexes its embeddings for semantic search.
    """
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded.")
    if not file.content_type or file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type. Only PDF and DOCX are allowed.")

    try:
        db_resume = await resume_service.process_and_store_resume(db, file)
        return db_resume
    except resume_service.ResumeServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

@router.get("/{resume_id}", response_model=resume_schemas.ResumeResponse)
async def get_single_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves details of a specific resume by its ID.
    """
    db_resume = await resume_service.get_resume_by_id(db, resume_id)
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return db_resume

@router.get("/", response_model=List[resume_schemas.ResumeResponse])
async def get_all_resumes(
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of all uploaded resumes.
    """
    # For now, just return all resumes. For a real app, you'd add pagination.
    resumes = db.query(models.Resume).all()
    return resumes