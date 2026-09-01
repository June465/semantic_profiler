from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    username: Mapped[str] = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = Column(String(255), nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Resume(Base):

    __tablename__ = "resumes"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = Column(String(255), index=True, nullable=False)
    parsed_text: Mapped[str] = Column(Text, nullable=False)
    upload_date: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    evaluation_results: Mapped[List["EvaluationResult"]] = relationship("EvaluationResult", back_populates="resume")

    def __repr__(self):
        return f"<Resume(id={self.id}, filename='{self.filename}')>"


class JobDescription(Base):

    __tablename__ = "job_descriptions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[Optional[str]] = Column(String(255), nullable=True)
    description: Mapped[str] = Column(Text, nullable=False)
    upload_date: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    evaluation_results: Mapped[List["EvaluationResult"]] = relationship("EvaluationResult", back_populates="job_description")

    def __repr__(self):
        return f"<JobDescription(id={self.id}, title='{self.title or 'N/A'}')>"


class EvaluationResult(Base):

    __tablename__ = "evaluation_results"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description_id: Mapped[int] = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    candidate_name: Mapped[str] = Column(String(255), nullable=False, server_default="Unknown Candidate")
    
    overall_score: Mapped[float] = Column(Float, nullable=False)
    strengths: Mapped[list] = Column(JSON, nullable=False)    
    weaknesses: Mapped[list] = Column(JSON, nullable=False)   
    summary: Mapped[str] = Column(Text, nullable=False)
    score_breakdown: Mapped[dict] = Column(JSON, nullable=True)
    
    anonymized_score: Mapped[Optional[float]] = Column(Float, nullable=True)
    score_discrepancy: Mapped[Optional[float]] = Column(Float, nullable=True)
    bias_flag: Mapped[Optional[bool]] = Column(Boolean, nullable=True, default=False)
    
    percentile_rank: Mapped[Optional[float]] = Column(Float, nullable=True)

    evaluation_date: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="evaluation_results")
    job_description: Mapped["JobDescription"] = relationship("JobDescription", back_populates="evaluation_results")

    def __repr__(self):
        return f"<EvaluationResult(id={self.id}, resume_id={self.resume_id}, score={self.overall_score})>"