import unittest
import numpy as np
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

import faiss

import backend.core.vector_store as vector_module
from backend.core.vector_store import (
    initialize_faiss_index, load_faiss_index_and_mapping,
    save_faiss_index_and_mapping, add_embeddings_to_index, search_index,
    VectorStoreError
)

TEST_DIR = Path("test_faiss_data")
TEST_INDEX_PATH = TEST_DIR / "test_resume_index.faiss"
TEST_METADATA_PATH = TEST_DIR / "test_resume_metadata.json"

# Helper to ensure global state is truly reset
def reset_vector_store_globals():
    vector_module._faiss_index = None
    vector_module._metadata_mapping = []
    vector_module._index_file_path = None
    vector_module._metadata_file_path = None

class TestVectorStore(unittest.TestCase):

    EMBEDDING_DIM = 384

    @classmethod
    def setUpClass(cls):
        TEST_DIR.mkdir(exist_ok=True)
        print(f"\n[Test Setup] Created test directory: {TEST_DIR}")
        # Note: set_index_paths is now ONLY called directly in setUp, not setUpClass.

    @classmethod
    def tearDownClass(cls):
        if TEST_DIR.exists():
            import shutil
            shutil.rmtree(TEST_DIR)
            print(f"\n[Test Teardown] Removed test directory: {TEST_DIR}")
        reset_vector_store_globals()


    def setUp(self):
        # 1. Ensure globals are clean from previous test (important for isolation)
        reset_vector_store_globals()

        # 2. Explicitly set the global paths for the vector_module here
        # This is CRUCIAL for persistence logic to work in most tests.
        vector_module._index_file_path = str(TEST_INDEX_PATH)
        vector_module._metadata_file_path = str(TEST_METADATA_PATH)

        # 3. Clean any existing test files to ensure a fresh state for file operations
        if TEST_INDEX_PATH.exists():
            TEST_INDEX_PATH.unlink()
        if TEST_METADATA_PATH.exists():
            TEST_METADATA_PATH.unlink()

        # 4. Initialize a real FAISS index for most tests
        self.test_index = initialize_faiss_index(self.EMBEDDING_DIM)
        vector_module._faiss_index = self.test_index
        vector_module._metadata_mapping = []

        # 5. Dummy data
        self.dummy_embeddings = np.random.rand(5, self.EMBEDDING_DIM).astype('float32')
        self.dummy_metadata = [
            {"id": 1, "text": "chunk 1"}, {"id": 2, "text": "chunk 2"},
            {"id": 3, "text": "chunk 3"}, {"id": 4, "text": "chunk 4"},
            {"id": 5, "text": "chunk 5"},
        ]
        self.dummy_query_embedding = np.random.rand(self.EMBEDDING_DIM).astype('float32')


    # --- Test initialize_faiss_index --- (NO CHANGES HERE, already passing)
    def test_initialize_faiss_index_flatl2(self):
        index = initialize_faiss_index(self.EMBEDDING_DIM, "FlatL2")
        self.assertIsInstance(index, faiss.IndexFlatL2)
        self.assertEqual(index.d, self.EMBEDDING_DIM)
        self.assertEqual(index.ntotal, 0)

    def test_initialize_faiss_index_unsupported_type(self):
        with self.assertRaisesRegex(VectorStoreError, "Unsupported FAISS index type"):
            initialize_faiss_index(self.EMBEDDING_DIM, "IVFFlat")

    def test_initialize_faiss_index_invalid_dimension(self):
        with self.assertRaisesRegex(ValueError, "Embedding dimension must be a positive integer"):
            initialize_faiss_index(0)

    # --- Test add_embeddings_to_index ---
    def test_add_embeddings_to_index_success(self):
        add_embeddings_to_index(self.dummy_embeddings, self.dummy_metadata)
        self.assertEqual(self.test_index.ntotal, len(self.dummy_embeddings))
        self.assertEqual(len(vector_module._metadata_mapping), len(self.dummy_metadata))
        self.assertEqual(vector_module._metadata_mapping[0]['id'], 1)
        # Verify persistence implicitly happened (files should exist)
        self.assertTrue(TEST_INDEX_PATH.exists())
        self.assertTrue(TEST_METADATA_PATH.exists())


    def test_add_embeddings_to_index_no_init_index(self):
        reset_vector_store_globals() # Clear all globals
        # IMPORTANT: Do not set paths here, to test the truly uninitialized state
        with self.assertRaisesRegex(VectorStoreError, "FAISS index is not initialized"):
            add_embeddings_to_index(self.dummy_embeddings, self.dummy_metadata)

    def test_add_embeddings_to_index_dimension_mismatch(self):
        mismatched_embeddings = np.random.rand(5, self.EMBEDDING_DIM + 1).astype('float32')
        with self.assertRaisesRegex(VectorStoreError, "Embedding dimension mismatch"):
            add_embeddings_to_index(mismatched_embeddings, self.dummy_metadata)

    def test_add_embeddings_to_index_count_mismatch(self):
        mismatched_metadata = self.dummy_metadata[:-1]
        with self.assertRaisesRegex(ValueError, "Number of embeddings must match number of metadata entries."):
            add_embeddings_to_index(self.dummy_embeddings, mismatched_metadata)

    @patch('backend.core.vector_store.save_faiss_index_and_mapping')
    def test_add_embeddings_to_index_persists_automatically(self, mock_save):
        add_embeddings_to_index(self.dummy_embeddings, self.dummy_metadata)
        mock_save.assert_called_once_with(self.test_index, vector_module._metadata_mapping, str(TEST_INDEX_PATH), str(TEST_METADATA_PATH))

    @patch('backend.core.vector_store.save_faiss_index_and_mapping')
    def test_add_embeddings_to_index_no_persistence_if_paths_not_set(self, mock_save):
        # Clear paths *after* setUp has run for this specific test
        vector_module._index_file_path = None
        vector_module._metadata_file_path = None
        add_embeddings_to_index(self.dummy_embeddings, self.dummy_metadata)
        mock_save.assert_not_called()


    # --- Test save_faiss_index_and_mapping ---
    def test_save_faiss_index_and_mapping_success(self):
        # No need to call add_embeddings_to_index if we are testing save_faiss_index_and_mapping directly.
        # Ensure index has some data
        self.test_index.add(self.dummy_embeddings)
        vector_module._metadata_mapping.extend(self.dummy_metadata)

        # Call the save function directly
        save_faiss_index_and_mapping(self.test_index, vector_module._metadata_mapping, str(TEST_INDEX_PATH), str(TEST_METADATA_PATH))

        self.assertTrue(TEST_INDEX_PATH.exists())
        self.assertTrue(TEST_METADATA_PATH.exists())
        with open(TEST_METADATA_PATH, 'r') as f:
            loaded_meta = json.load(f)
            self.assertEqual(len(loaded_meta), len(self.dummy_metadata))
            self.assertEqual(loaded_meta[0]['id'], self.dummy_metadata[0]['id'])

    @patch('faiss.write_index', side_effect=Exception("FAISS write error"))
    def test_save_faiss_index_failure(self, mock_write_index):
        # Ensure metadata file exists, as save_faiss_index_and_mapping attempts to write metadata too
        with open(TEST_METADATA_PATH, 'w') as f:
            json.dump([], f) # Create an empty JSON file
        with self.assertRaisesRegex(VectorStoreError, "FAISS write error"):
            save_faiss_index_and_mapping(self.test_index, self.dummy_metadata, str(TEST_INDEX_PATH), str(TEST_METADATA_PATH))


    # --- Test load_faiss_index_and_mapping ---
    def test_load_faiss_index_and_mapping_success(self):
        self.test_index.add(self.dummy_embeddings) # <--- ADD THIS LINE!
        # Ensure metadata mapping is also populated for saving
        vector_module._metadata_mapping.extend(self.dummy_metadata) # <--- ADD THIS LINE!
        # First, ensure files exist on disk from a previous save
        save_faiss_index_and_mapping(self.test_index, self.dummy_metadata, str(TEST_INDEX_PATH), str(TEST_METADATA_PATH))

        reset_vector_store_globals() # Clear globals before loading
        # Ensure paths are set globally for the load function
        vector_module._index_file_path = str(TEST_INDEX_PATH)
        vector_module._metadata_file_path = str(TEST_METADATA_PATH)

        loaded_index, loaded_metadata = load_faiss_index_and_mapping(str(TEST_INDEX_PATH), str(TEST_METADATA_PATH))
        self.assertIsInstance(loaded_index, faiss.Index)
        self.assertEqual(loaded_index.ntotal, len(self.dummy_embeddings))
        self.assertEqual(len(loaded_metadata), len(self.dummy_metadata))
        self.assertIs(vector_module._faiss_index, loaded_index)
        self.assertIs(vector_module._metadata_mapping, loaded_metadata)

    def test_load_faiss_index_file_not_found(self):
        with open(TEST_METADATA_PATH, 'w') as f:
            json.dump([], f)
        with self.assertRaisesRegex(VectorStoreError, "FAISS index file not found"):
            load_faiss_index_and_mapping("non_existent.faiss", str(TEST_METADATA_PATH))

    def test_load_metadata_file_not_found(self):
        faiss.write_index(initialize_faiss_index(self.EMBEDDING_DIM), str(TEST_INDEX_PATH))
        with self.assertRaisesRegex(VectorStoreError, "Metadata file not found"):
            load_faiss_index_and_mapping(str(TEST_INDEX_PATH), "non_existent.json")

    @patch('faiss.read_index', side_effect=Exception("FAISS read error"))
    def test_load_faiss_index_failure(self, mock_read_index):
        # Ensure files exist for the load function to proceed to faiss.read_index
        save_faiss_index_and_mapping(self.test_index, self.dummy_metadata, str(TEST_INDEX_PATH), str(TEST_METADATA_PATH))
        reset_vector_store_globals() # Clear globals before loading
        # Ensure paths are set globally for the load function
        vector_module._index_file_path = str(TEST_INDEX_PATH)
        vector_module._metadata_file_path = str(TEST_METADATA_PATH)

        with self.assertRaisesRegex(VectorStoreError, "FAISS read error"):
            load_faiss_index_and_mapping(str(TEST_INDEX_PATH), str(TEST_METADATA_PATH))


    # --- Test search_index ---
    def test_search_index_success(self):
        add_embeddings_to_index(self.dummy_embeddings, self.dummy_metadata)
        results = search_index(self.dummy_query_embedding, k=2)
        self.assertEqual(len(results), 2)
        self.assertIn('text', results[0])
        self.assertIn('distance', results[0])
        self.assertLessEqual(results[0]['distance'], results[1]['distance'])

    def test_search_index_no_init_index(self):
        reset_vector_store_globals()
        # Ensure no index is initialized and global paths are also cleared
        vector_module._faiss_index = None
        vector_module._index_file_path = None
        vector_module._metadata_file_path = None
        with self.assertRaisesRegex(VectorStoreError, "FAISS index is not initialized"):
            search_index(self.dummy_query_embedding)

    def test_search_index_query_dimension_mismatch(self):
        mismatched_query = np.random.rand(self.EMBEDDING_DIM + 1).astype('float32')
        add_embeddings_to_index(self.dummy_embeddings, self.dummy_metadata)
        with self.assertRaisesRegex(VectorStoreError, "Query embedding dimension mismatch"):
            search_index(mismatched_query)

    def test_search_index_empty_index_returns_empty_list(self):
        # Index is initialized but empty from setUp
        results = search_index(self.dummy_query_embedding, k=2)
        self.assertEqual(len(results), 0)

    def test_search_index_k_greater_than_total(self):
        embeddings_for_test = self.dummy_embeddings[:2]
        metadata_for_test = self.dummy_metadata[:2]
        add_embeddings_to_index(embeddings_for_test, metadata_for_test)
        results = search_index(self.dummy_query_embedding, k=5)
        self.assertEqual(len(results), 2)

if __name__ == '__main__':
    unittest.main()