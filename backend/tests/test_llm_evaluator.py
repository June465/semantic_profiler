import unittest
import json
import os
from unittest.mock import patch, MagicMock, call
import backend.core.llm_evaluator as llm_module
from backend.core.llm_evaluator import (
    construct_evaluation_prompt, call_llm_for_evaluation,
    initialize_deepseek_client, LLMEvaluationError # <--- CHANGE: initialize_deepseek_client
)
import openai # <--- Import OpenAI client for mocking
from openai import APIError # <--- Import APIError from openai directly


# Helper to reset global client state for isolation
def reset_deepseek_client_state(): # <--- CHANGE: Renamed function
    llm_module._deepseek_client = None


class TestLLMEvaluator(unittest.TestCase):

    def setUp(self):
        reset_deepseek_client_state() # <--- CHANGE: Call new reset function
        self.api_key = "test_api_key_123"
        self.job_description = "Seeking a Python developer for backend services."
        self.candidate_chunks = ["Experienced Python developer.", "Built scalable APIs."]
        self.deepseek_model_name = "deepseek-coder" # <--- NEW: Default model name for tests
        self.deepseek_base_url = "https://api.deepseek.com/v1" # <--- NEW: Base URL for tests

    # --- Test construct_evaluation_prompt --- (NO CHANGES HERE)
    def test_construct_evaluation_prompt_basic(self):
        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        self.assertIsInstance(prompt, str)
        self.assertIn(self.job_description.strip(), prompt)
        self.assertIn("Experienced Python developer.", prompt)
        self.assertIn("Built scalable APIs.", prompt)
        self.assertIn("JSON format", prompt)
        self.assertIn("overall_score", prompt)
        self.assertIn("strengths", prompt)
        self.assertIn("weaknesses", prompt)
        self.assertIn("summary", prompt)

    def test_construct_evaluation_prompt_empty_job_description(self):
        with self.assertRaises(ValueError) as cm:
            construct_evaluation_prompt("", self.candidate_chunks)
        self.assertIn("Job description and candidate chunks cannot be empty.", str(cm.exception))

    def test_construct_evaluation_prompt_empty_chunks(self):
        with self.assertRaises(ValueError) as cm:
            construct_evaluation_prompt(self.job_description, [])
        self.assertIn("Job description and candidate chunks cannot be empty.", str(cm.exception))

    def test_construct_evaluation_prompt_whitespace_chunks(self):
        chunks = ["  ", "  \n  "]
        prompt = construct_evaluation_prompt(self.job_description, chunks)
        self.assertIn("CANDIDATE'S RELEVANT RESUME SNIPPETS: ---", prompt) # Adjusted assertion
        self.assertNotIn("  ", prompt)


    # --- Test initialize_deepseek_client --- # <--- CHANGE: Renamed tests
    @patch('openai.OpenAI') # <--- CHANGE: Patch openai.OpenAI directly
    def test_initialize_deepseek_client_success(self, MockOpenAI): # <--- CHANGE: Renamed mock
        mock_client_instance = MockOpenAI.return_value # <--- CHANGE: Client instance

        client = initialize_deepseek_client(self.api_key, self.deepseek_base_url) # <--- CHANGE: Call new init function

        MockOpenAI.assert_called_once_with( # <--- CHANGE: Assert call to OpenAI constructor
            api_key=self.api_key,
            base_url=self.deepseek_base_url,
        )
        self.assertIs(client, mock_client_instance)
        self.assertIs(llm_module._deepseek_client, client) # <--- CHANGE: Check global _deepseek_client


    @patch('openai.OpenAI', side_effect=Exception("API client init error")) # <--- CHANGE: Patch openai.OpenAI
    def test_initialize_deepseek_client_failure(self, MockOpenAI): # <--- CHANGE: Renamed mock
        with self.assertRaisesRegex(LLMEvaluationError, "Failed to initialize Deepseek client: API client init error"):
            initialize_deepseek_client(self.api_key, self.deepseek_base_url) # <--- CHANGE: Call new init function
        self.assertIsNone(llm_module._deepseek_client) # <--- CHANGE: Check global _deepseek_client


    @patch('openai.OpenAI') # <--- CHANGE: Patch openai.OpenAI
    def test_initialize_deepseek_client_singleton_behavior(self, MockOpenAI): # <--- CHANGE: Renamed mock
        reset_deepseek_client_state() # <--- CHANGE: Call new reset function

        mock_client_instance = MagicMock()
        MockOpenAI.return_value = mock_client_instance

        first_call = initialize_deepseek_client(self.api_key, self.deepseek_base_url) # <--- CHANGE: Call new init function
        MockOpenAI.assert_called_once_with(
            api_key=self.api_key,
            base_url=self.deepseek_base_url,
        )
        self.assertIs(first_call, mock_client_instance)
        self.assertIs(llm_module._deepseek_client, mock_client_instance) # <--- CHANGE: Check global _deepseek_client

        MockOpenAI.reset_mock() # <--- CHANGE: Reset MockOpenAI, not MockConfigure
        MockOpenAI.reset_mock() # No need to reset MockConfigure if it's not patched directly

        second_call = initialize_deepseek_client(self.api_key, self.deepseek_base_url) # <--- CHANGE: Call new init function
        MockOpenAI.assert_not_called()
        self.assertIs(first_call, second_call)


    # --- Test call_llm_for_evaluation ---

    @patch('backend.core.llm_evaluator.initialize_deepseek_client') # <--- CHANGE: Patch initialize_deepseek_client
    def test_call_llm_for_evaluation_success(self, mock_initialize_deepseek_client): # <--- CHANGE: Renamed mock
        mock_client_instance = MagicMock()
        mock_initialize_deepseek_client.return_value = mock_client_instance

        mock_completion_response = MagicMock() # Mock the completion object
        mock_choice = MagicMock()
        expected_json = {
            "overall_score": 85,
            "strengths": ["Python expertise", "Scalable API development"],
            "weaknesses": ["None identified"],
            "summary": "Strong candidate with relevant experience."
        }
        mock_choice.message.content = json.dumps(expected_json)
        mock_completion_response.choices = [mock_choice] # Deepseek/OpenAI returns list of choices
        
        mock_client_instance.chat.completions.create.return_value = mock_completion_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        result = call_llm_for_evaluation(prompt, self.api_key, self.deepseek_model_name)

        mock_initialize_deepseek_client.assert_called_once_with(self.api_key) # <--- Default base_url is used internally
        mock_client_instance.chat.completions.create.assert_called_once_with(
            model=self.deepseek_model_name, # <--- Model name passed here
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        self.assertEqual(result, expected_json)


    @patch('backend.core.llm_evaluator.initialize_deepseek_client')
    def test_call_llm_for_evaluation_malformed_json(self, mock_initialize_deepseek_client):
        mock_client_instance = MagicMock()
        mock_initialize_deepseek_client.return_value = mock_client_instance

        mock_completion_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "{not valid json"
        mock_completion_response.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_completion_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "Failed to parse LLM response as JSON"):
            call_llm_for_evaluation(prompt, self.api_key, self.deepseek_model_name)


    @patch('backend.core.llm_evaluator.initialize_deepseek_client')
    def test_call_llm_for_evaluation_empty_response(self, mock_initialize_deepseek_client):
        mock_client_instance = MagicMock()
        mock_initialize_deepseek_client.return_value = mock_client_instance

        mock_completion_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = ""
        mock_completion_response.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_completion_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "Deepseek LLM returned an empty response."):
            call_llm_for_evaluation(prompt, self.api_key, self.deepseek_model_name)


    @patch('backend.core.llm_evaluator.initialize_deepseek_client')
    def test_call_llm_for_evaluation_api_error(self, mock_initialize_deepseek_client):
        mock_client_instance = MagicMock()
        mock_initialize_deepseek_client.return_value = mock_client_instance

        # Mock the specific OpenAI APIError type
        mock_client_instance.chat.completions.create.side_effect = APIError("Quota exceeded", None, None) # <--- Use APIError from openai

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, r"Deepseek API error during evaluation: Quota exceeded"):
            call_llm_for_evaluation(prompt, self.api_key, self.deepseek_model_name)


    @patch('backend.core.llm_evaluator.initialize_deepseek_client')
    def test_call_llm_for_evaluation_missing_keys(self, mock_initialize_deepseek_client):
        mock_client_instance = MagicMock()
        mock_initialize_deepseek_client.return_value = mock_client_instance

        mock_completion_response = MagicMock()
        mock_choice = MagicMock()
        malformed_json = {"overall_score": 70, "summary": "Missing strengths/weaknesses"}
        mock_choice.message.content = json.dumps(malformed_json)
        mock_completion_response.choices = [mock_choice]
        mock_client_instance.chat.completions.create.return_value = mock_completion_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "LLM response missing expected keys"):
            call_llm_for_evaluation(prompt, self.api_key, self.deepseek_model_name)


    def test_call_llm_for_evaluation_no_api_key(self):
        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "Deepseek API key is not provided."):
            call_llm_for_evaluation(prompt, "", self.deepseek_model_name)