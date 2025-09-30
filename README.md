# semantic_profiler

Okay, excellent choice! Switching to Google's Gemini LLM is straightforward and mainly involves changing the client library and API key handling.

Let's adjust the relevant steps in our guide for using Gemini.

Phase 0: Project Setup and Foundation (Revisit)

Step 0.4: Install Core Dependencies (Backend) - Adjusted for Gemini

Goal: Install essential Python libraries, specifically for Gemini.

Procedure:

Update requirements.txt:

Remove openai from your requirements.txt.

Add google-generativeai.

Your requirements.txt should now look something like this:

code
Code
download
content_copy
expand_less
fastapi
uvicorn[standard]
SQLAlchemy
pymysql
python-dotenv
pdfplumber
python-docx
langchain
sentence-transformers
faiss-cpu
google-generativeai # <-- New dependency for Gemini

Install Dependencies: With your virtual environment activated:

code
Bash
download
content_copy
expand_less
pip install -r requirements.txt
Phase 1: Core Engine Development (Revisit)

Step 1.5: LLM Integration Module (backend/core/llm_evaluator.py) - Adjusted for Gemini

Goal: Functions to construct LLM prompts and call the Gemini LLM for evaluation.

Procedure:

Create backend/core/llm_evaluator.py: (If you already created it, you'll be modifying it).

Define construct_evaluation_prompt(job_description: str, candidate_chunks: List[str]) -> str function:

This function remains largely the same. The prompt structure for Gemini will be very similar to what you'd use for OpenAI. You still want clear instructions, the job description, candidate chunks, and a request for a specific output format (e.g., JSON).

Example Prompt Template (within your function):

code
Python
download
content_copy
expand_less
prompt_template = f"""
You are an expert HR recruiter evaluating a candidate for a job opening.
Your task is to analyze the provided job description and relevant candidate resume snippets, then provide a comprehensive evaluation.

---
JOB DESCRIPTION:
{job_description}
---

CANDIDATE RESUME SNIPPETS:
{"\n\n".join(candidate_chunks)}
---

Please provide the following in a JSON format:
1.  `overall_score`: An integer representing the candidate's overall fit (0-100).
2.  `strengths`: A list of bullet points highlighting the candidate's key strengths relevant to the job.
3.  `weaknesses`: A list of bullet points identifying any gaps or areas where the candidate might not meet requirements based *only* on the provided information.
4.  `summary`: A concise paragraph summarizing the candidate's suitability for the role.

Ensure your response is valid JSON.
"""
return prompt_template

Define call_llm_for_evaluation(prompt: str, api_key: str, model_name: str = "gemini-pro") -> Dict function:

Input: The prompt, your Gemini API key, and the Gemini model name (e.g., "gemini-pro").

Logic:

Import the library: import google.generativeai as genai

Configure the API key: genai.configure(api_key=api_key)

Load the model: model = genai.GenerativeModel(model_name)

Make the API call:

Gemini's generate_content method is used. You can directly pass the prompt.

Consider using safety_settings if you need to adjust content filtering.

The response object will have a text attribute containing the LLM's generated string.

Error Handling: Implement try-except for network errors, API key issues, or issues with the model's response (e.g., if it fails to generate content or returns an unparseable response).

Response Parsing: The response.text will be a string. Since you've asked for JSON, you'll need to parse this string into a Python dictionary: import json; results = json.loads(response.text). Handle json.JSONDecodeError.

Return: A dictionary containing the parsed evaluation results.

Example Snippet for call_llm_for_evaluation (you'll adapt and integrate this):

code
Python
download
content_copy
expand_less
import google.generativeai as genai
import json
import os

def call_llm_for_evaluation(prompt: str, api_key: str, model_name: str = "gemini-pro") -> Dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    try:
        # You might need to adjust safety settings or add generation_config
        # For strict JSON, you might need extra prompting or re-try logic if it deviates.
        response = model.generate_content(prompt)
        raw_text = response.text
        # Clean up potential markdown formatting (e.g., ```json ... ```)
        if raw_text.strip().startswith("```json") and raw_text.strip().endswith("```"):
            raw_text = raw_text.strip()[7:-3].strip() # Remove ```json and ```

        evaluation_results = json.loads(raw_text)
        return evaluation_results
    except Exception as e:
        # Log the error, maybe log the raw_text for debugging
        print(f"Error calling Gemini LLM or parsing response: {e}")
        # Optionally, return a default error structure or re-raise
        raise

Test Locally:

Get a job description and some retrieved chunks.

Construct a prompt.

Ensure your Gemini API key is set (e.g., in an environment variable GOOGLE_API_KEY that your script can access, or passed directly for testing).

Call the LLM.

Print the parsed output.

Phase 4: Dockerization and Local Deployment (Revisit)

Step 4.2: Update docker/docker-compose.yml - Adjusted for Gemini

Goal: Ensure the backend container has access to your Gemini API key.

Procedure:

Modify docker/docker-compose.yml:

In the backend service, change the environment variable name from OPENAI_API_KEY to GOOGLE_API_KEY (or whatever you decide to name it, just be consistent).

Make sure GOOGLE_API_KEY: ${GOOGLE_API_KEY} is present.

code
Yaml
download
content_copy
expand_less
version: '3.8'

services:
  # ... db service ...

  backend:
    build:
      context: ../
      dockerfile: docker/backend.Dockerfile
    container_name: fastapi_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: mysql+pymysql://user:password@db:3306/semantic_profiler_db
      GOOGLE_API_KEY: ${GOOGLE_API_KEY} # <-- Changed for Gemini
      # Other environment variables like FAISS index path, model path
    depends_on:
      - db
    networks:
      - app_network
    volumes:
      - ./faiss_index_data:/app/faiss_data

  # ... frontend service ...

volumes:
  db_data:
  faiss_index_data:

networks:
  app_network:
    driver: bridge

Environment Variables: Create or update your .env file in your project root:

code
Code
download
content_copy
expand_less
GOOGLE_API_KEY=your_gemini_api_key_here

How to get a Gemini API Key: You'll need to go to the Google AI Studio (or Google Cloud Console, if you prefer, but AI Studio is simpler for quick starts) and create an API key. Search for "Google AI Studio" or "Gemini API Key".

Step 4.3: Local Testing with Docker Compose - Verify Gemini Integration

Goal: Run your entire application stack and ensure Gemini is being used.

Procedure:

Build and Run (from docker/ directory):

code
Bash
download
content_copy
expand_less
docker-compose build
docker-compose up -d

Verify:

Check docker-compose logs backend to ensure no errors related to google-generativeai or missing API keys.

Test the flow via your frontend or Swagger UI. The evaluation should now be powered by Gemini.

This change is mainly focused on the llm_evaluator.py file and setting the correct API key as an environment variable. The rest of your project structure and API endpoints remain the same, demonstrating the modularity of the design!