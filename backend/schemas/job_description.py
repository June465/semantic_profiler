from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class JobDescriptionBase(BaseModel):
    description: str = Field(..., description="The full text of the job description.")
    title: Optional[str] = Field(None, description="Optional title for the job description.")

class JobDescriptionCreate(JobDescriptionBase):
    pass

class JobDescriptionResponse(JobDescriptionBase):
    id: int = Field(..., description="Unique ID of the job description.")
    upload_date: datetime = Field(..., description="Timestamp of when the job description was submitted.")

    class Config:
        from_attributes = True