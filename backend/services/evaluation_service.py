from sqlalchemy.orm import Session
import os
from typing import List, Optional, Tuple
import numpy as np

from backend.database import models
from backend.core import embedding_generator, vector_store, llm_evaluator, bias_module

BIAS_DISCREPANCY_THRESHOLD = 10.0

class EvaluationServiceError(Exception):
    pass

def calculate_percentiles(evaluations: List[models.EvaluationResult]) -> List[models.EvaluationResult]:

    if not evaluations:
        return []

    scores = np.array([e.overall_score for e in evaluations if e.overall_score is not None])
    if len(scores) == 0:
        return evaluations

    for eval_result in evaluations:
        if eval_result.overall_score is not None:
            less_than_count = np.sum(scores < eval_result.overall_score)
            equal_to_count = np.sum(scores == eval_result.overall_score)
            
            rank = (less_than_count + 0.5 * equal_to_count) / len(scores) * 100
            eval_result.percentile_rank = round(rank, 2)
            
    return evaluations

async def perform_evaluation(
    db: Session,
    job_description_text: str,
    resume_ids: List[int],
    job_title: Optional[str] = None
) -> Tuple[List[models.EvaluationResult], List[int]]:
    if not job_description_text or not resume_ids:
        raise ValueError("Job description and a list of resume IDs are required.")

    db_job_description = models.JobDescription(description=job_description_text, title=job_title)
    db.add(db_job_description)

    db.flush()
    
    embedding_model = embedding_generator.initialize_embedding_model()

    job_description_embedding = embedding_generator.get_embeddings(job_description_text, embedding_model)

    temp_evaluated_results: List[models.EvaluationResult] = []
    skipped_ids: List[int] = []

    for resume_id in resume_ids:
        db_resume = db.query(models.Resume).filter(models.Resume.id == resume_id).first()
        if not db_resume:
            print(f"Warning: Resume with ID {resume_id} not found. Skipping.")
            continue

        try:
            relevant_chunks_metadata = vector_store.search_index(job_description_embedding, k=10)
            candidate_specific_chunks = [m['chunk_text'] for m in relevant_chunks_metadata if m.get('resume_id') == resume_id]
            if not candidate_specific_chunks:
                skipped_ids.append(resume_id)
                continue

            deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            if not deepseek_api_key:
                raise EvaluationServiceError("DEEPSEEK_API_KEY is not set.")
            
            deepseek_model_name = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-coder")

            llm_prompt = llm_evaluator.construct_evaluation_prompt(job_description_text, candidate_specific_chunks)
            evaluation_output = llm_evaluator.call_llm_for_evaluation(
                llm_prompt, deepseek_api_key, model_name=deepseek_model_name
            )

            anonymized_chunks = bias_module.anonymize_chunks(candidate_specific_chunks)
            anonymized_llm_prompt = llm_evaluator.construct_evaluation_prompt(job_description_text, anonymized_chunks)
            anonymized_output = llm_evaluator.call_llm_for_evaluation(
                anonymized_llm_prompt, deepseek_api_key, model_name=deepseek_model_name
            )
            
            original_score = evaluation_output.get("overall_score")
            anonymized_score = anonymized_output.get("overall_score")

            score_discrepancy = None
            bias_flag = False
            if original_score is not None and anonymized_score is not None:
                score_discrepancy = abs(original_score - anonymized_score)
                if score_discrepancy > BIAS_DISCREPANCY_THRESHOLD:
                    bias_flag = True
            
            db_evaluation = models.EvaluationResult(
                resume_id=db_resume.id,
                job_description_id=db_job_description.id,
                candidate_name=evaluation_output.get("candidate_name", "Unknown Candidate"),
                overall_score=original_score,
                strengths=evaluation_output.get("strengths", []),
                weaknesses=evaluation_output.get("weaknesses", []),
                summary=evaluation_output.get("summary"),
                score_breakdown=evaluation_output.get("score_breakdown", {}),
                anonymized_score=anonymized_score,
                score_discrepancy=score_discrepancy,
                bias_flag=bias_flag
            )
            temp_evaluated_results.append(db_evaluation)
        except Exception as e:
            print(f"Evaluation failed for resume {resume_id}: {e}")
            skipped_ids.append(resume_id)

    if temp_evaluated_results:
        final_results_with_percentiles = calculate_percentiles(temp_evaluated_results)
        db.add_all(final_results_with_percentiles)
        db.commit()
        for result in final_results_with_percentiles:
            db.refresh(result)
        return final_results_with_percentiles, skipped_ids

    db.commit()
    return [], skipped_ids

async def get_evaluation_results_by_id(db: Session, evaluation_id: int) -> Optional[models.EvaluationResult]:
    return db.query(models.EvaluationResult).filter(models.EvaluationResult.id == evaluation_id).first()

async def get_all_evaluations(db: Session) -> List[models.EvaluationResult]:
    return db.query(models.EvaluationResult).all()