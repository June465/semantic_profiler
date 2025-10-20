from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class EvaluationRequest(BaseModel):
    job_description: str = Field(..., description="The job description text for evaluation.")
    resume_ids: List[int] = Field(..., description="A list of resume IDs to evaluate.")
    job_title: Optional[str] = Field(None, description="Optional title for the job description.")

class EvaluationResultBase(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    summary: str

class EvaluationResultResponse(EvaluationResultBase):
    id: int
    resume_id: int
    job_description_id: int
    evaluation_date: datetime

    candidate_name: str = Field(..., description="The candidate's name as extracted by the AI.")
    
    class Config:
        from_attributes = True

class MassEvaluationResponse(BaseModel):
    successful_evaluations: List[EvaluationResultResponse] = Field(..., description="A list of successfully completed evaluations.")
    skipped_resume_ids: List[int] = Field(..., description="A list of resume IDs that were skipped due to lack of relevant information.")