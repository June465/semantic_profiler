import openai # <--- CHANGE: Import OpenAI client
import json
import os
import re
from typing import List, Dict, Any, Optional

# No longer need GoogleAPIError, use OpenAI's equivalent or general Exception
# from google.api_core.exceptions import GoogleAPIError

class LLMEvaluationError(Exception):
    """Custom exception for LLM evaluation failures."""
    pass

def construct_evaluation_prompt(job_description: str, candidate_chunks: List[str]) -> str:
    """
    Constructs a detailed prompt for the LLM to evaluate a candidate based on job description
    and relevant resume chunks.
    (This function's logic and the prompt template itself remain largely the same,
     as the desired output format for the LLM is independent of the provider.)
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
    1.  `overall_score`: An integer representing the candidate's overall fit (0-100).
    2.  `strengths`: A list of bullet points (each a string) highlighting the candidate's key strengths directly relevant to the job.
    3.  `weaknesses`: A list of bullet points (each a string) identifying any gaps or areas where the candidate might not fully meet requirements, based *only* on the provided information. If no significant weaknesses are found, state "None identified".
    4.  `summary`: A concise paragraph (string) summarizing the candidate's suitability for the role, drawing conclusions from both strengths and weaknesses.

    Ensure the output is valid JSON, and do not include any additional text or markdown formatting (e.g., ```json) outside the JSON object itself."""
    
    final_prompt = re.sub(r'\s+', ' ', prompt_template).strip()
    return final_prompt

# Global variable to store the Deepseek client, for efficient reuse
_deepseek_client: Optional[openai.OpenAI] = None

def initialize_deepseek_client(api_key: str, base_url: str = "https://api.deepseek.com/v1") -> openai.OpenAI:
    """
    Initializes and loads the Deepseek API client using OpenAI compatibility.
    The client is initialized only once (singleton pattern).

    Args:
        api_key (str): Your Deepseek API key.
        base_url (str): The base URL for the Deepseek API (default: https://api.deepseek.com/v1).

    Returns:
        openai.OpenAI: The initialized OpenAI-compatible Deepseek client.
    """
    global _deepseek_client
    if _deepseek_client is None:
        try:
            print(f"Initializing Deepseek client with base URL: {base_url}...")
            _deepseek_client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url,
            )
            print(f"Deepseek client initialized.")
        except Exception as e:
            print(f"Error initializing Deepseek client: {e}")
            raise LLMEvaluationError(f"Failed to initialize Deepseek client: {e}")
    return _deepseek_client


def call_llm_for_evaluation(prompt: str, api_key: str, model_name: str = "deepseek-coder") -> Dict[str, Any]:
    """
    Sends the constructed prompt to the Deepseek LLM for evaluation and parses the JSON response.

    Args:
        prompt (str): The detailed prompt for the LLM.
        api_key (str): Your Deepseek API key.
        model_name (str): The name of the Deepseek model to use (e.g., "deepseek-coder", "deepseek-chat").

    Returns:
        Dict[str, Any]: A dictionary containing the parsed evaluation results.

    Raises:
        LLMEvaluationError: If the LLM call fails, returns an invalid response,
                            or the JSON cannot be parsed.
    """
    if not api_key:
        raise LLMEvaluationError("Deepseek API key is not provided.")
    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    try:
        client = initialize_deepseek_client(api_key) # Gets singleton

        # Deepseek uses a messages array, similar to OpenAI's chat completions
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Adjust model_name as per Deepseek's available models
        # Common Deepseek models: "deepseek-coder", "deepseek-chat"
        # For JSON mode, ensure the model explicitly supports it or rely on strong prompting.
        # OpenAI client's `response_format` might work for Deepseek's API if they support it.
        # However, for broader compatibility, we'll parse text.
        
        # The .env file can specify `DEEPSEEK_MODEL_NAME` to override default
        model_to_use = os.getenv("DEEPSEEK_MODEL_NAME", model_name)

        completion = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=0.5, # Lower for more deterministic output
            # max_tokens=1000, # Max output tokens, Deepseek's API might have specific param name
            response_format={"type": "json_object"} # Use OpenAI client's JSON mode
        )

        response_content = completion.choices[0].message.content
        if not response_content:
            raise LLMEvaluationError("Deepseek LLM returned an empty response.")

        # Clean up potential markdown formatting (e.g., ```json ... ```)
        raw_text = response_content.strip()
        if raw_text.startswith("```json") and raw_text.endswith("```"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```") and raw_text.endswith("```"):
            raw_text = raw_text[3:-3].strip()

        evaluation_results = json.loads(raw_text)

        expected_keys = ["overall_score", "strengths", "weaknesses", "summary"]
        if not all(key in evaluation_results for key in expected_keys):
            raise LLMEvaluationError(f"LLM response missing expected keys. Expected: {expected_keys}, Got: {evaluation_results.keys()}. Raw response: {raw_text}")

        return evaluation_results

    except json.JSONDecodeError as e:
        raise LLMEvaluationError(f"Failed to parse LLM response as JSON: {e}. Raw response: {raw_text}")
    except openai.APIError as e: # <--- CHANGE: Catch OpenAI.APIError
        raise LLMEvaluationError(f"Deepseek API error during evaluation: {e}")
    except Exception as e:
        raise LLMEvaluationError(f"An unexpected error occurred during LLM evaluation: {e}")


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print("--- Testing llm_evaluator functions locally with Deepseek ---")

    # IMPORTANT: Set your DEEPSEEK_API_KEY in a .env file or as an environment variable
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1") # Default base URL
    DEEPSEEK_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-coder") # Default model name

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