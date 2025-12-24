from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ResumeBase(BaseModel):
    filename: str = Field(..., description="Original filename of the resume.")

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: int = Field(..., description="Unique ID of the resume.")
    parsed_text: str = Field(..., description="The full parsed text of the resume.")
    upload_date: datetime = Field(..., description="Timestamp of when the resume was uploaded.")
    
    class Config:
        from_attributes = True