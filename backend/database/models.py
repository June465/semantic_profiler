from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped 
from datetime import datetime
from typing import List, Optional

Base = declarative_base()

class Resume(Base):
    """
    SQLAlchemy model for storing resume information.
    """
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True, nullable=False)
    parsed_text = Column(Text, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    evaluation_results: Mapped[List["EvaluationResult"]] = relationship("EvaluationResult", back_populates="resume")

    def __repr__(self):
        return f"<Resume(id={self.id}, filename='{self.filename}')>"


class JobDescription(Base):
    """
    SQLAlchemy model for storing job description information.
    """
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    evaluation_results: Mapped[List["EvaluationResult"]] = relationship("EvaluationResult", back_populates="job_description")

    def __repr__(self):
        return f"<JobDescription(id={self.id}, title='{self.title or 'N/A'}')>"


class EvaluationResult(Base):
    """
    SQLAlchemy model for storing the results of an LLM-powered evaluation.
    """
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)

    overall_score = Column(Float, nullable=False)
    strengths = Column(Text, nullable=False)
    weaknesses = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    evaluation_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="evaluation_results") 
    job_description: Mapped["JobDescription"] = relationship("JobDescription", back_populates="evaluation_results") 

    def __repr__(self):
        return f"<EvaluationResult(id={self.id}, resume_id={self.resume_id}, score={self.overall_score})>"