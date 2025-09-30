from sqlalchemy.orm import Session
import json
import os
from typing import List, Dict, Any, Optional 

from backend.database import models
from backend.core import embedding_generator, vector_store, llm_evaluator

class EvaluationServiceError(Exception):
    """Custom exception for evaluation service failures."""
    pass

async def perform_evaluation(
    db: Session,
    job_description_text: str,
    resume_ids: List[int],
    job_title: Optional[str] = None # Uses Optional
) -> List[models.EvaluationResult]:
    """
    Performs LLM-powered evaluations for multiple candidates against a job description.

    Args:
        db (Session): SQLAlchemy database session.
        job_description_text (str): The text of the job description.
        resume_ids (List[int]): List of IDs for resumes to evaluate.
        job_title (Optional[str]): An optional title for the job description.

    Returns:
        List[models.EvaluationResult]: A list of created EvaluationResult database objects.

    Raises:
        EvaluationServiceError: If any step in the evaluation process fails.
        ValueError: If input is invalid.
    """
    if not job_description_text or not resume_ids:
        raise ValueError("Job description and a list of resume IDs are required.")

    # 1. Create JobDescription entry in database
    db_job_description = models.JobDescription(description=job_description_text, title=job_title)
    db.add(db_job_description)
    db.commit()
    db.refresh(db_job_description)

    # 2. Embed Job Description for retrieval
    embedding_model = embedding_generator.initialize_embedding_model()
    job_description_embedding = embedding_generator.get_embeddings(job_description_text, embedding_model)

    evaluated_results: List[models.EvaluationResult] = []

    for resume_id in resume_ids:
        db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
        if not db_resume:
            print(f"Warning: Resume with ID {resume_id} not found. Skipping evaluation.")
            continue

        try:
            relevant_chunks_metadata = vector_store.search_index(
                job_description_embedding,
                k=10
            )

            candidate_specific_chunks = [
                m['chunk_text'] for m in relevant_chunks_metadata
                if m.get('resume_id') == resume_id
            ]

            if not candidate_specific_chunks:
                print(f"Warning: No relevant chunks found in FAISS for resume ID {resume_id} for this job. Skipping LLM evaluation.")
                continue

            llm_prompt = llm_evaluator.construct_evaluation_prompt(
                job_description_text, candidate_specific_chunks
            )

            # Get Deepseek API key and model name from environment
            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise EvaluationServiceError("DEEPSEEK_API_KEY is not set for LLM evaluation.")
            deepseek_model_name = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-coder") # Default model name

            evaluation_output = llm_evaluator.call_llm_for_evaluation(
                llm_prompt, deepseek_api_key, model_name=deepseek_model_name # Pass model name
            )

            db_evaluation = models.EvaluationResult(
                resume_id=db_resume.id,
                job_description_id=db_job_description.id,
                overall_score=evaluation_output.get("overall_score"),
                strengths=json.dumps(evaluation_output.get("strengths", [])),
                weaknesses=json.dumps(evaluation_output.get("weaknesses", [])),
                summary=evaluation_output.get("summary")
            )
            db.add(db_evaluation)
            db.commit()
            db.refresh(db_evaluation)
            evaluated_results.append(db_evaluation)

        except llm_evaluator.LLMEvaluationError as e:
            db.rollback()
            raise EvaluationServiceError(f"LLM evaluation failed for resume {resume_id}: {e}")
        except embedding_generator.LLMEvaluationError as e:
            db.rollback()
            raise EvaluationServiceError(f"Embedding model error for resume {resume_id}: {e}")
        except vector_store.VectorStoreError as e:
            db.rollback()
            raise EvaluationServiceError(f"Vector store (FAISS) error for resume {resume_id}: {e}")
        except Exception as e:
            db.rollback()
            raise EvaluationServiceError(f"An unexpected error occurred during evaluation of resume {resume_id}: {e}")

    return evaluated_results


async def get_evaluation_results_by_id(db: Session, evaluation_id: int) -> Optional[models.EvaluationResult]:
    """
    Retrieves a specific evaluation result by its ID.
    Also fetches associated resume and job description.
    """
    evaluation = db.query(models.EvaluationResult).filter(models.EvaluationResult.id == evaluation_id).first()
    if evaluation:
        # Convert JSON strings back to lists for Pydantic serialization
        evaluation.strengths = json.loads(evaluation.strengths)
        evaluation.weaknesses = json.loads(evaluation.weaknesses)
    return evaluation

async def get_all_evaluations(db: Session) -> List[models.EvaluationResult]:
    """
    Retrieves all evaluation results.
    """
    evaluations = db.query(models.EvaluationResult).all()
    for evaluation in evaluations:
        if evaluation.strengths:
            evaluation.strengths = json.loads(evaluation.strengths)
        if evaluation.weaknesses:
            evaluation.weaknesses = json.loads(evaluation.weaknesses)
    return evaluations