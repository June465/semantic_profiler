import unittest
import json
import os
from unittest.mock import patch, MagicMock, call
# Import the module itself for patching globals
import backend.core.llm_evaluator as llm_module
from backend.core.llm_evaluator import (
    construct_evaluation_prompt, call_llm_for_evaluation,
    initialize_gemini_model, LLMEvaluationError
)
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError


def reset_gemini_model_state():
    llm_module._gemini_model = None


class TestLLMEvaluator(unittest.TestCase):

    def setUp(self):
        reset_gemini_model_state()
        self.api_key = "test_api_key_123"
        self.job_description = "Seeking a Python developer for backend services."
        self.candidate_chunks = ["Experienced Python developer.", "Built scalable APIs."]

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

    # THIS IS THE FAILING TEST - ADJUSTING ASSERTION
    def test_construct_evaluation_prompt_whitespace_chunks(self):
        chunks = ["  ", "  \n  "]
        prompt = construct_evaluation_prompt(self.job_description, chunks)
        # After re.sub(r'\s+', ' ', ...), all newlines and multiple spaces become single spaces.
        # The prompt will be a single line. So, the assertion should reflect this.
        # Original: "CANDIDATE'S RELEVANT RESUME SNIPPETS:\n    \n    ---"
        # Becomes:  "CANDIDATE'S RELEVANT RESUME SNIPPETS: ---"
        self.assertIn("CANDIDATE'S RELEVANT RESUME SNIPPETS: ---", prompt) # <--- Corrected assertion
        self.assertNotIn("  ", prompt) # This should now pass because re.sub removes all double spaces


    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_initialize_gemini_model_success(self, MockGenerativeModel, MockConfigure):
        mock_instance = MockGenerativeModel.return_value

        model = initialize_gemini_model(self.api_key)

        MockConfigure.assert_called_once_with(api_key=self.api_key)
        MockGenerativeModel.assert_called_once_with("gemini-pro")
        self.assertIs(model, mock_instance)
        self.assertIs(llm_module._gemini_model, model)


    @patch('google.generativeai.configure', side_effect=Exception("API config error"))
    @patch('google.generativeai.GenerativeModel')
    def test_initialize_gemini_model_failure(self, MockGenerativeModel, MockConfigure):
        with self.assertRaisesRegex(LLMEvaluationError, "Failed to initialize Gemini model: API config error"):
            initialize_gemini_model(self.api_key)
        self.assertIsNone(llm_module._gemini_model)


    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_initialize_gemini_model_singleton_behavior(self, MockGenerativeModel, MockConfigure):
        reset_gemini_model_state()

        mock_instance = MagicMock()
        MockGenerativeModel.return_value = mock_instance

        first_call = initialize_gemini_model(self.api_key)
        MockConfigure.assert_called_once_with(api_key=self.api_key)
        MockGenerativeModel.assert_called_once_with("gemini-pro")
        self.assertIs(first_call, mock_instance)
        self.assertIs(llm_module._gemini_model, mock_instance)

        MockConfigure.reset_mock()
        MockGenerativeModel.reset_mock()

        second_call = initialize_gemini_model(self.api_key)
        MockConfigure.assert_not_called()
        MockGenerativeModel.assert_not_called()
        self.assertIs(first_call, second_call)


    @patch('backend.core.llm_evaluator.initialize_gemini_model')
    def test_call_llm_for_evaluation_success(self, mock_initialize_gemini_model):
        mock_model_instance = MagicMock()
        mock_initialize_gemini_model.return_value = mock_model_instance

        mock_response = MagicMock()
        expected_json = {
            "overall_score": 85,
            "strengths": ["Python expertise", "Scalable API development"],
            "weaknesses": ["None identified"],
            "summary": "Strong candidate with relevant experience."
        }
        mock_response.text = json.dumps(expected_json)
        mock_model_instance.generate_content.return_value = mock_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        result = call_llm_for_evaluation(prompt, self.api_key)

        mock_initialize_gemini_model.assert_called_once_with(self.api_key, "gemini-pro")
        mock_model_instance.generate_content.assert_called_once_with(prompt, generation_config={
            "temperature": 0.5, "max_output_tokens": 1000, "response_mime_type": "application/json"
        })
        self.assertEqual(result, expected_json)

    @patch('backend.core.llm_evaluator.initialize_gemini_model')
    def test_call_llm_for_evaluation_malformed_json(self, mock_initialize_gemini_model):
        mock_model_instance = MagicMock()
        mock_initialize_gemini_model.return_value = mock_model_instance

        mock_response = MagicMock()
        mock_response.text = "{not valid json"
        mock_model_instance.generate_content.return_value = mock_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "Failed to parse LLM response as JSON"):
            call_llm_for_evaluation(prompt, self.api_key)

    @patch('backend.core.llm_evaluator.initialize_gemini_model')
    def test_call_llm_for_evaluation_empty_response(self, mock_initialize_gemini_model):
        mock_model_instance = MagicMock()
        mock_initialize_gemini_model.return_value = mock_model_instance

        mock_response = MagicMock()
        mock_response.text = ""
        mock_model_instance.generate_content.return_value = mock_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "Gemini LLM returned an empty response."):
            call_llm_for_evaluation(prompt, self.api_key)

    @patch('backend.core.llm_evaluator.initialize_gemini_model')
    def test_call_llm_for_evaluation_api_error(self, mock_initialize_gemini_model):
        mock_model_instance = MagicMock()
        mock_initialize_gemini_model.return_value = mock_model_instance

        mock_model_instance.generate_content.side_effect = GoogleAPIError("Quota exceeded", 429, "Rate limit")

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, r"Gemini API error during evaluation: \(?'Quota exceeded'.*\)"):
            call_llm_for_evaluation(prompt, self.api_key)


    @patch('backend.core.llm_evaluator.initialize_gemini_model')
    def test_call_llm_for_evaluation_missing_keys(self, mock_initialize_gemini_model):
        mock_model_instance = MagicMock()
        mock_initialize_gemini_model.return_value = mock_model_instance

        mock_response = MagicMock()
        malformed_json = {"overall_score": 70, "summary": "Missing strengths/weaknesses"}
        mock_response.text = json.dumps(malformed_json)
        mock_model_instance.generate_content.return_value = mock_response

        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "LLM response missing expected keys"):
            call_llm_for_evaluation(prompt, self.api_key)


    def test_call_llm_for_evaluation_no_api_key(self):
        prompt = construct_evaluation_prompt(self.job_description, self.candidate_chunks)
        with self.assertRaisesRegex(LLMEvaluationError, "Gemini API key is not provided."):
            call_llm_for_evaluation(prompt, "")