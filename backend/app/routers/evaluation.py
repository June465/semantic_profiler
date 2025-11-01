from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.database import get_db
from backend.services import evaluation_service
from backend.core.security import get_current_user
from backend.schemas import evaluation as schemas

router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"],
)

@router.post("/", response_model=schemas.MassEvaluationResponse, status_code=status.HTTP_200_OK)
async def create_evaluation(
    evaluation_input: schemas.EvaluationRequest, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Create a new evaluation for one or more resumes against a job description.
    Returns successful evaluations and a list of any skipped resume IDs.
    """
    try:
        successful_results, skipped_ids = await evaluation_service.perform_evaluation(
            db=db,
            job_description_text=evaluation_input.job_description,
            job_title=evaluation_input.job_title,
            resume_ids=evaluation_input.resume_ids
        )
        
        return {
            "successful_evaluations": successful_results,
            "skipped_resume_ids": skipped_ids
        }
        
    except evaluation_service.EvaluationServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{evaluation_id}", response_model=schemas.EvaluationResultResponse)
async def get_single_evaluation_result(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves the detailed results of a specific candidate evaluation.
    """
    evaluation = await evaluation_service.get_evaluation_results_by_id(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation result not found.")
    return evaluation

@router.get("/", response_model=List[schemas.EvaluationResultResponse])
async def get_all_evaluation_results(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieves a list of all performed evaluation results.
    """
    evaluations = await evaluation_service.get_all_evaluations(db)
    return evaluations