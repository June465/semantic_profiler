import openai
import json
import os
import re
from typing import List, Dict, Any, Optional

class LLMEvaluationError(Exception):
    """Custom exception for LLM evaluation failures."""
    pass

def construct_evaluation_prompt(job_description: str, candidate_chunks: List[str]) -> str:
    """
    Constructs a detailed prompt for the LLM to evaluate a candidate.
    """
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
    1.  "candidate_name": A string containing the candidate's full name as extracted from the resume snippets. If the name cannot be clearly identified, return "Unknown Candidate".
    2.  "overall_score": An integer representing the candidate's overall fit (0-100).
    3.  "strengths": A list of bullet points (each a string) highlighting the candidate's key strengths.
    4.  "weaknesses": A list of bullet points (each a string) identifying any gaps or areas of concern.
    5.  "summary": A concise paragraph (string) summarizing the candidate's suitability for the role.

    Ensure the output is a single, valid JSON object and nothing else.
    """
   
    final_prompt = re.sub(r'\s+', ' ', prompt_template).strip()
    return final_prompt

_deepseek_client: Optional[openai.OpenAI] = None
def initialize_deepseek_client(api_key: str, base_url: str = "https://api.deepseek.com/v1") -> openai.OpenAI:
    global _deepseek_client
    if _deepseek_client is None:
        try:
            _deepseek_client = openai.OpenAI(api_key=api_key, base_url=base_url)
        except Exception as e:
            raise LLMEvaluationError(f"Failed to initialize Deepseek client: {e}")
    return _deepseek_client

def call_llm_for_evaluation(prompt: str, api_key: str, model_name: str = "deepseek-coder") -> Dict[str, Any]:
    """
    Sends the constructed prompt to the Deepseek LLM and parses the JSON response.
    """
    if not api_key:
        raise LLMEvaluationError("Deepseek API key is not provided.")
    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    try:
        client = initialize_deepseek_client(api_key)
        messages = [{"role": "user", "content": prompt}]
        model_to_use = os.getenv("DEEPSEEK_MODEL_NAME", model_name)

        completion = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        response_content = completion.choices[0].message.content
        if not response_content:
            raise LLMEvaluationError("Deepseek LLM returned an empty response.")

        raw_text = response_content.strip()
        evaluation_results = json.loads(raw_text)

        expected_keys = ["candidate_name", "overall_score", "strengths", "weaknesses", "summary"]
        if not all(key in evaluation_results for key in expected_keys):
            raise LLMEvaluationError(f"LLM response missing expected keys. Got: {evaluation_results.keys()}. Raw: {raw_text}")

        return evaluation_results

    except json.JSONDecodeError as e:
        raise LLMEvaluationError(f"Failed to parse LLM response as JSON: {e}. Raw response: {raw_text if 'raw_text' in locals() else 'N/A'}")
    except openai.APIError as e:
        raise LLMEvaluationError(f"Deepseek API error during evaluation: {e}")
    except Exception as e:
        raise LLMEvaluationError(f"An unexpected error occurred during LLM evaluation: {e}")

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print("--- Testing llm_evaluator functions locally with Deepseek ---")

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-coder") 

    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY environment variable not set. Cannot run live LLM test.")
        print("Please create a .env file in your project root with DEEPSEEK_API_KEY=YOUR_DEEPSEEK_API_KEY")
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

            print("\n--- Calling Deepseek LLM (Live API Call) ---")
            evaluation_result = call_llm_for_evaluation(prompt, DEEPSEEK_API_KEY, DEEPSEEK_MODEL_NAME)

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