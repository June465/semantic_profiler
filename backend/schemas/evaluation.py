from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict

class EvaluationRequest(BaseModel):
    job_description: str = Field(..., description="The job description text for evaluation.")
    resume_ids: List[int] = Field(..., description="A list of resume IDs to evaluate.")
    job_title: Optional[str] = Field(None, description="Optional title for the job description.")

ScoreBreakdown = Dict[str, float]

class EvaluationResultBase(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    summary: str
    score_breakdown: Optional[ScoreBreakdown] = Field(None, description="Detailed breakdown of scores by category.")

class EvaluationResultResponse(EvaluationResultBase):
    id: int
    resume_id: int
    job_description_id: int
    evaluation_date: datetime
    candidate_name: str = Field(..., description="The candidate's name as extracted by the AI.")
    
    anonymized_score: Optional[float] = Field(None, description="Score from the anonymized evaluation.")
    score_discrepancy: Optional[float] = Field(None, description="Absolute difference between original and anonymized scores.")
    bias_flag: bool = Field(False, description="Flag indicating if the score discrepancy exceeds a set threshold.")
    
    percentile_rank: Optional[float] = Field(None, ge=0, le=100, description="The candidate's score percentile rank within the batch.")

    class Config:
        from_attributes = True

class MassEvaluationResponse(BaseModel):
    successful_evaluations: List[EvaluationResultResponse] = Field(..., description="A list of successfully completed evaluations.")
    skipped_resume_ids: List[int] = Field(..., description="A list of resume IDs that were skipped due to lack of relevant information.")