from sqlalchemy.orm import Session
import os
from typing import List, Dict, Any, Optional, Tuple

from backend.database import models
from backend.core import embedding_generator, vector_store, llm_evaluator

class EvaluationServiceError(Exception):
    """Custom exception for evaluation service failures."""
    pass

async def perform_evaluation(
    db: Session,
    job_description_text: str,
    resume_ids: List[int],
    job_title: Optional[str] = None
) -> Tuple[List[models.EvaluationResult], List[int]]:
    """
    Performs LLM evaluations and returns both successful results and skipped resume IDs.
    """
    if not job_description_text or not resume_ids:
        raise ValueError("Job description and a list of resume IDs are required.")

    db_job_description = models.JobDescription(description=job_description_text, title=job_title)
    db.add(db_job_description)
    db.commit()
    db.refresh(db_job_description)

    embedding_model = embedding_generator.initialize_embedding_model()
    job_description_embedding = embedding_generator.get_embeddings(job_description_text, embedding_model)

    evaluated_results: List[models.EvaluationResult] = []
    skipped_ids: List[int] = []

    for resume_id in resume_ids:
        db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
        if not db_resume:
            print(f"Warning: Resume with ID {resume_id} not found. Skipping.")
            continue

        try:
            relevant_chunks_metadata = vector_store.search_index(job_description_embedding, k=10)
            candidate_specific_chunks = [
                m['chunk_text'] for m in relevant_chunks_metadata
                if m.get('resume_id') == resume_id
            ]
            if not candidate_specific_chunks:
                print(f"Warning: No relevant chunks for resume ID {resume_id}. Skipping.")
                skipped_ids.append(resume_id)
                continue

            llm_prompt = llm_evaluator.construct_evaluation_prompt(
                job_description_text, candidate_specific_chunks
            )

            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise EvaluationServiceError("DEEPSEEK_API_KEY is not set.")
            
            deepseek_model_name = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-coder")

            evaluation_output = llm_evaluator.call_llm_for_evaluation(
                llm_prompt, deepseek_api_key, model_name=deepseek_model_name
            )

            db_evaluation = models.EvaluationResult(
                resume_id=db_resume.id,
                job_description_id=db_job_description.id,
                candidate_name=evaluation_output.get("candidate_name", "Unknown Candidate"),
                overall_score=evaluation_output.get("overall_score"),
                strengths=evaluation_output.get("strengths", []),  
                weaknesses=evaluation_output.get("weaknesses", []), 
                summary=evaluation_output.get("summary")
            )
            
            db.add(db_evaluation)
            db.commit()
            db.refresh(db_evaluation)
            evaluated_results.append(db_evaluation)

        except (llm_evaluator.LLMEvaluationError, vector_store.VectorStoreError) as e:
            db.rollback()
            raise EvaluationServiceError(f"Evaluation failed for resume {resume_id}: {e}")
        except Exception as e:
            db.rollback()
            raise EvaluationServiceError(f"Unexpected error for resume {resume_id}: {e}")

    return evaluated_results, skipped_ids

async def get_evaluation_results_by_id(db: Session, evaluation_id: int) -> Optional[models.EvaluationResult]:
    return db.query(models.EvaluationResult).filter(models.EvaluationResult.id == evaluation_id).first()

async def get_all_evaluations(db: Session) -> List[models.EvaluationResult]:
    return db.query(models.EvaluationResult).all()