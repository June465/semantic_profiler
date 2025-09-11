import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from typing import Optional, List

from sentence_transformers import SentenceTransformer

import backend.core.embedding_generator as embedding_module
from backend.core.embedding_generator import (
    initialize_embedding_model, get_embeddings, get_embedding_dimension
)

def reset_embedding_model_state():
    embedding_module._embedding_model = None
    embedding_module._embedding_dimension = None

class TestEmbeddingGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        reset_embedding_model_state()
        try:
            cls.model_instance = initialize_embedding_model("all-MiniLM-L6-v2")
            cls.embedding_dim = get_embedding_dimension()
            print(f"\n[Test Setup] Model loaded, dimension: {cls.embedding_dim}")
        except Exception as e:
            cls.fail(f"Failed to load embedding model in setUpClass: {e}")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # ... (other tests - test_initialize_embedding_model_singleton, test_get_embedding_dimension, etc. - should remain as they were in the last successful version) ...

    def test_get_embeddings_single_text(self):
        text = "This is a test sentence."
        embedding = get_embeddings(text, self.model_instance)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (self.embedding_dim,))

    def test_get_embeddings_list_of_texts(self):
        texts = ["Sentence one.", "Sentence two.", "Sentence three."]
        embeddings = get_embeddings(texts, self.model_instance)
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape, (len(texts), self.embedding_dim))
        self.assertIsInstance(embeddings[0], np.ndarray)

    def test_get_embeddings_empty_list(self):
        embeddings = get_embeddings([], self.model_instance)
        self.assertIsInstance(embeddings, list)
        self.assertEqual(len(embeddings), 0)

    def test_get_embeddings_empty_string(self):
        embedding = get_embeddings("", self.model_instance)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.size, 0)

    def test_get_embeddings_with_none_model(self):
        with self.assertRaises(AttributeError) as cm:
             get_embeddings("text", None)
        self.assertIn("'NoneType' object has no attribute 'encode'", str(cm.exception))


    @patch.object(embedding_module, '_embedding_model', new=None) # Explicitly ensures global is None for this test
    @patch.object(embedding_module, '_embedding_dimension', new=None) # Explicitly ensures global is None for this test
    @patch('backend.core.embedding_generator.SentenceTransformer')
    def test_initialize_embedding_model_failure(self, MockSentenceTransformer):
        reset_embedding_model_state() # Defensive, patches above should handle this.
        MockSentenceTransformer.side_effect = Exception("Mock loading error during init")

        with self.assertRaisesRegex(Exception, "Mock loading error during init"):
            initialize_embedding_model("non-existent-model")

        self.assertIsNone(embedding_module._embedding_model)
        self.assertIsNone(embedding_module._embedding_dimension)


    # THIS IS THE TEST WE ARE FOCUSING ON:
    @patch('backend.core.embedding_generator.SentenceTransformer') # Patch the class where it's imported in the module
    def test_get_embeddings_failure_during_encode(self, MockSentenceTransformerClass):
        """Test error handling during embedding generation (encode method fails)."""
        # We need to simulate a *successfully loaded* model whose .encode() method fails.
        # So, first ensure the global _embedding_model is set to a mock instance.
        # For this, we'll initialize the model via our function, but it will use the MockSentenceTransformerClass.
        reset_embedding_model_state() # Ensure globals are clean for this specific test

        # Configure the mock class to return a mock instance
        mock_instance = MagicMock(spec=SentenceTransformer)
        MockSentenceTransformerClass.return_value = mock_instance

        # Call initialize_embedding_model to set the global _embedding_model to our mock_instance
        _ = initialize_embedding_model("dummy-model-name") # The actual name doesn't matter here

        # Now, _embedding_model in embedding_generator is our mock_instance.
        # Set its 'encode' method to raise an exception.
        mock_instance.encode.side_effect = Exception("Mock encoding error from encode method")

        # Call get_embeddings with the global _embedding_model (which is our mock_instance)
        with self.assertRaisesRegex(Exception, "Mock encoding error from encode method"):
            get_embeddings("some text", embedding_module._embedding_model)

        # Verify that the encode method was indeed called on the mock instance
        mock_instance.encode.assert_called_once()
        # Verify the SentenceTransformer constructor was called once by initialize_embedding_model
        MockSentenceTransformerClass.assert_called_once_with("dummy-model-name")


    def test_get_embeddings_before_model_initialized(self):
        """Test get_embeddings when the global model has not been initialized yet."""
        reset_embedding_model_state() # Clear state
        with self.assertRaises(AttributeError) as cm:
            get_embeddings("some text", embedding_module._embedding_model) # Now embedding_module._embedding_model is None
        self.assertIn("'NoneType' object has no attribute 'encode'", str(cm.exception))

if __name__ == '__main__':
    unittest.main()