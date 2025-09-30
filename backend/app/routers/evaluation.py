from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.database import get_db
from backend.services import evaluation_service
from backend.schemas import evaluation as evaluation_schemas # Use alias
from backend.database import models

# Create an API router for evaluation-related endpoints
router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"],
)

@router.post("/", response_model=List[evaluation_schemas.EvaluationResultResponse], status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    request: evaluation_schemas.EvaluationRequest,
    db: Session = Depends(get_db)
):
    """
    Initiates an LLM-powered evaluation of multiple resumes against a given job description.
    """
    try:
        evaluation_results = await evaluation_service.perform_evaluation(
            db,
            request.job_description,
            request.resume_ids,
            request.job_title
        )
        if not evaluation_results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No evaluations could be performed for the given resumes/job description (e.g., resumes not found or no relevant chunks)."
            )
        return evaluation_results
    except evaluation_service.EvaluationServiceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

@router.get("/{evaluation_id}", response_model=evaluation_schemas.EvaluationResultResponse)
async def get_single_evaluation_result(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves the detailed results of a specific candidate evaluation.
    """
    evaluation = await evaluation_service.get_evaluation_results_by_id(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation result not found.")
    return evaluation

@router.get("/", response_model=List[evaluation_schemas.EvaluationResultResponse])
async def get_all_evaluation_results(
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of all performed evaluation results.
    """
    evaluations = await evaluation_service.get_all_evaluations(db)
    return evaluations