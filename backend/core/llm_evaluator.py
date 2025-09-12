import google.generativeai as genai
import json
import os
import re 
from typing import List, Dict, Any, Optional
from google.api_core.exceptions import GoogleAPIError

class LLMEvaluationError(Exception):
    """Custom exception for LLM evaluation failures."""
    pass

def construct_evaluation_prompt(job_description: str, candidate_chunks: List[str]) -> str:
    if not job_description or not candidate_chunks:
        raise ValueError("Job description and candidate chunks cannot be empty.")

    candidate_profile = "\n\n".join(chunk.strip() for chunk in candidate_chunks if chunk.strip())

    prompt_template = f"""
    You are an expert HR recruiter assistant. Your task is to evaluate a candidate's suitability for a job
    based on the provided job description and relevant resume snippets.
    Analyze the information thoroughly and provide a comprehensive evaluation.

    ---
    JOB DESCRIPTION:
    {job_description.strip()}
    ---

    CANDIDATE'S RELEVANT RESUME SNIPPETS:
    {candidate_profile}
    ---

    Please provide your evaluation in a JSON format with the following keys:
    1.  `overall_score`: An integer representing the candidate's overall fit (0-100).
    2.  `strengths`: A list of bullet points (each a string) highlighting the candidate's key strengths directly relevant to the job.
    3.  `weaknesses`: A list of bullet points (each a string) identifying any gaps or areas where the candidate might not fully meet requirements, based *only* on the provided information. If no significant weaknesses are found, state "None identified".
    4.  `summary`: A concise paragraph (string) summarizing the candidate's suitability for the role, drawing conclusions from both strengths and weaknesses.

    Ensure the output is valid JSON, and do not include any additional text or markdown formatting (e.g., ```json) outside the JSON object itself."""

    final_prompt = re.sub(r'\s+', ' ', prompt_template).strip()
    return final_prompt

# Global variable to store the loaded Gemini model, for efficient reuse
_gemini_model: Optional[genai.GenerativeModel] = None

def initialize_gemini_model(api_key: str, model_name: str = "gemini-pro") -> genai.GenerativeModel:
    global _gemini_model
    if _gemini_model is None:
        try:
            print(f"Initializing Google Gemini model: {model_name}...")
            genai.configure(api_key=api_key)
            _gemini_model = genai.GenerativeModel(model_name)
            print(f"Gemini model '{model_name}' initialized.")
        except Exception as e:
            print(f"Error initializing Gemini model '{model_name}': {e}")
            raise LLMEvaluationError(f"Failed to initialize Gemini model: {e}")
    return _gemini_model


def call_llm_for_evaluation(prompt: str, api_key: str, model_name: str = "gemini-pro") -> Dict[str, Any]:
    if not api_key:
        raise LLMEvaluationError("Gemini API key is not provided.")
    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    try:
        model = initialize_gemini_model(api_key, model_name)

        generation_config = {
            "temperature": 0.5,
            "max_output_tokens": 1000,
            "response_mime_type": "application/json"
        }

        response = model.generate_content(prompt, generation_config=generation_config)

        if not response.text:
            raise LLMEvaluationError("Gemini LLM returned an empty response.")

        raw_text = response.text.strip()
        if raw_text.startswith("```json") and raw_text.endswith("```"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```") and raw_text.endswith("```"):
            raw_text = raw_text[3:-3].strip()

        evaluation_results = json.loads(raw_text)

        expected_keys = ["overall_score", "strengths", "weaknesses", "summary"]
        if not all(key in evaluation_results for key in expected_keys):
            raise LLMEvaluationError(f"LLM response missing expected keys. Expected: {expected_keys}, Got: {evaluation_results.keys()}")

        return evaluation_results

    except json.JSONDecodeError as e:
        raise LLMEvaluationError(f"Failed to parse LLM response as JSON: {e}. Raw response: {raw_text}")
    except GoogleAPIError as e: # <--- Make sure this is GoogleAPIError
        raise LLMEvaluationError(f"Gemini API error during evaluation: {e}")
    except Exception as e:
        raise LLMEvaluationError(f"An unexpected error occurred during LLM evaluation: {e}")


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print("--- Testing llm_evaluator functions locally with Gemini ---")

    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

    if not GEMINI_API_KEY:
        print("ERROR: GOOGLE_API_KEY environment variable not set. Cannot run live LLM test.")
        print("Please create a .env file in your project root with GOOGLE_API_KEY=YOUR_GEMINI_API_KEY")
    else:
        sample_job_description = """
        We are seeking a highly motivated Senior Software Engineer with 5+ years of experience
        in building scalable backend services using Python, FastAPI, and PostgreSQL.
        Experience with AWS, Docker, and Kubernetes is required.
        Leadership skills and experience mentoring junior developers are a strong plus.
        """
        sample_candidate_chunks = [
            "John Doe, Senior Software Engineer. 7 years experience.",
            "Led a team of 4 junior developers at TechCorp (2020-Present).",
            "Developed RESTful APIs using Python and FastAPI, deployed on AWS EKS.",
            "Expert in PostgreSQL, Docker, and CI/CD pipelines."
        ]

        print("\n--- Constructing Prompt ---")
        try:
            prompt = construct_evaluation_prompt(sample_job_description, sample_candidate_chunks)
            print(f"Prompt length: {len(prompt)} characters. First 500 chars:\n'{prompt[:500]}...'")

            print("\n--- Calling Gemini LLM (Live API Call) ---")
            evaluation_result = call_llm_for_evaluation(prompt, GEMINI_API_KEY)

            print("\n--- LLM Evaluation Result ---")
            print(json.dumps(evaluation_result, indent=2))

            assert "overall_score" in evaluation_result and isinstance(evaluation_result["overall_score"], int)
            assert "strengths" in evaluation_result and isinstance(evaluation_result["strengths"], list)
            assert "weaknesses" in evaluation_result and isinstance(evaluation_result["weaknesses"], list)
            assert "summary" in evaluation_result and isinstance(evaluation_result["summary"], str)
            print("\nLive LLM test completed and verified successfully!")

        except LLMEvaluationError as e:
            print(f"LLM Evaluation Error: {e}")
        except ValueError as e:
            print(f"Input Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during live test: {e}")