from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any

class EvaluationRequest(BaseModel):
    job_description: str = Field(..., description="The job description text for evaluation.")
    resume_ids: List[int] = Field(..., description="A list of resume IDs to evaluate against the job description.")
    job_title: Optional[str] = Field(None, description="Optional title for the job description (if not provided, backend might infer or leave empty).")


class EvaluationResultBase(BaseModel):
    overall_score: float = Field(..., ge=0, le=100, description="Overall fit score (0-100) for the candidate.")
    strengths: List[str] = Field(..., description="List of key strengths relevant to the job.")
    weaknesses: List[str] = Field(..., description="List of identified gaps or weaknesses.")
    summary: str = Field(..., description="Concise summary of candidate's suitability.")

class EvaluationResultResponse(EvaluationResultBase):
    id: int = Field(..., description="Unique ID of the evaluation result.")
    resume_id: int = Field(..., description="ID of the evaluated resume.")
    job_description_id: int = Field(..., description="ID of the job description used for evaluation.")
    evaluation_date: datetime = Field(..., description="Timestamp of when the evaluation was performed.")

    class Config:
        from_attributes = True
        # For strengths/weaknesses (Text in DB, List[str] in Pydantic),
        # Pydantic will attempt to convert. If stored as JSON string in DB,
        # you might need a custom serializer/deserializer if `orm_mode` doesn't handle it.
        # For now, `Text` field and `List[str]` in Pydantic will work if the LLM output is clean JSON.