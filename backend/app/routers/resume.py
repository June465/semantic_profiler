import os
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.database import get_db
from backend.services import resume_service
from backend.schemas import resume as resume_schemas 
from backend.database import models
from backend.core.security import get_current_user

RESUME_UPLOAD_DIR = "/app/uploaded_resumes"

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)

@router.post("/", response_model=resume_schemas.ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="The resume file to upload (PDF or DOCX)."),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
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
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
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
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves a list of all uploaded resumes.
    """
    resumes = db.query(models.Resume).all()
    return resumes

@router.get("/{resume_id}/file", response_class=FileResponse)
async def get_resume_file(
    resume_id: int, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found in database.")

    file_path = os.path.join(RESUME_UPLOAD_DIR, db_resume.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found on disk at path: {file_path}")
        
    return FileResponse(path=file_path, filename=db_resume.filename)