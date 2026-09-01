import faiss
import numpy as np
import os
import json
from typing import List, Dict, Tuple, Optional

_faiss_index: Optional[faiss.Index] = None
_metadata_mapping: List[Dict] = []
_index_file_path: Optional[str] = None
_metadata_file_path: Optional[str] = None

class VectorStoreError(Exception):
    pass

def initialize_faiss_index(embedding_dimension: int, index_type: str = "FlatL2") -> faiss.Index:
    if embedding_dimension <= 0:
        raise ValueError("Embedding dimension must be a positive integer.")

    if index_type == "FlatL2":
        return faiss.IndexFlatL2(embedding_dimension)
    else:
        raise VectorStoreError(f"Unsupported FAISS index type: {index_type}. Only 'FlatL2' is supported for now.")

def get_faiss_index_and_mapping() -> Tuple[Optional[faiss.Index], List[Dict]]:

    global _faiss_index, _metadata_mapping
    return _faiss_index, _metadata_mapping

def set_index_paths(index_path: str, metadata_path: str):

    global _index_file_path, _metadata_file_path
    _index_file_path = index_path
    _metadata_file_path = metadata_path

def load_faiss_index_and_mapping(index_path: str, metadata_path: str) -> Tuple[faiss.Index, List[Dict]]:

    global _faiss_index, _metadata_mapping, _index_file_path, _metadata_file_path
    if not os.path.exists(index_path):
        raise VectorStoreError(f"FAISS index file not found: {index_path}")
    if not os.path.exists(metadata_path):
        raise VectorStoreError(f"Metadata file not found: {metadata_path}")

    try:
        print(f"Loading FAISS index from {index_path}...")
        loaded_index = faiss.read_index(index_path)
        print(f"FAISS index loaded. Contains {loaded_index.ntotal} vectors.")

        print(f"Loading metadata mapping from {metadata_path}...")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            loaded_metadata = json.load(f)
        print(f"Metadata loaded. Contains {len(loaded_metadata)} entries.")

        _faiss_index = loaded_index
        _metadata_mapping = loaded_metadata
        _index_file_path = index_path
        _metadata_file_path = metadata_path

        return loaded_index, loaded_metadata
    except Exception as e:
        raise VectorStoreError(f"Failed to load FAISS index or metadata: {e}")

def save_faiss_index_and_mapping(index: faiss.Index, metadata: List[Dict], index_path: str, metadata_path: str) -> None:

    try:
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        faiss.write_index(index, index_path)
        print(f"FAISS index saved to {index_path}")

        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"Metadata mapping saved to {metadata_path}")
    except Exception as e:
        raise VectorStoreError(f"Failed to save FAISS index or metadata: {e}")

def add_embeddings_to_index(embeddings: np.ndarray, metadata: List[Dict]) -> None:

    global _faiss_index, _metadata_mapping, _index_file_path, _metadata_file_path

    if _faiss_index is None:
        raise VectorStoreError("FAISS index is not initialized. Call initialize_faiss_index or load_faiss_index_and_mapping first.")

    if not isinstance(embeddings, np.ndarray) or embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D NumPy array.")
    if embeddings.shape[1] != _faiss_index.d:
        raise VectorStoreError(f"Embedding dimension mismatch: expected {_faiss_index.d}, got {embeddings.shape[1]}")
    if len(embeddings) != len(metadata):
        raise ValueError("Number of embeddings must match number of metadata entries.")

    try:
        _faiss_index.add(embeddings)
        _metadata_mapping.extend(metadata)
        print(f"Added {len(embeddings)} embeddings to index. Total vectors: {_faiss_index.ntotal}")

        if _index_file_path and _metadata_file_path:
            save_faiss_index_and_mapping(_faiss_index, _metadata_mapping, _index_file_path, _metadata_file_path)
        else:
            print("Warning: Index paths not set, changes not persisted automatically.")

    except Exception as e:
        raise VectorStoreError(f"Error adding embeddings to FAISS index: {e}")

def search_index(query_embedding: np.ndarray, k: int = 5) -> List[Dict]:

    global _faiss_index, _metadata_mapping

    if _faiss_index is None:
        raise VectorStoreError("FAISS index is not initialized. Call initialize_faiss_index or load_faiss_index_and_mapping first.")

    if not isinstance(query_embedding, np.ndarray) or query_embedding.ndim != 1:
        raise ValueError("Query embedding must be a 1D NumPy array.")
    if query_embedding.shape[0] != _faiss_index.d:
        raise VectorStoreError(f"Query embedding dimension mismatch: expected {_faiss_index.d}, got {query_embedding.shape[0]}")

    try:
        distances, indices = _faiss_index.search(np.array([query_embedding]), k)

        results = []
        for i, idx in enumerate(indices[0]): 
            if idx == -1: 
                continue
            metadata = _metadata_mapping[idx]
            metadata['distance'] = float(distances[0][i])
            results.append(metadata)

        return results
    except IndexError:
        print("Warning: FAISS index contains fewer elements than k. Returning available results.")
        return results
    except Exception as e:
        raise VectorStoreError(f"Error during FAISS search: {e}")

if __name__ == '__main__':
    print("--- Testing vector_store functions locally ---")

    dummy_resume_chunks = [
        {"resume_id": 1, "chunk_id": "r1_c1", "chunk_text": "Experienced software engineer with 5 years in Python development."},
        {"resume_id": 1, "chunk_id": "r1_c2", "chunk_text": "Led a team of 3 junior developers in an Agile environment."},
        {"resume_id": 1, "chunk_id": "r1_c3", "chunk_text": "Skills include FastAPI, Docker, AWS, and PostgreSQL."},
        {"resume_id": 2, "chunk_id": "r2_c1", "chunk_text": "Frontend developer specializing in React and JavaScript frameworks."},
        {"resume_id": 2, "chunk_id": "r2_c2", "chunk_text": "Designed and implemented user interfaces for SaaS products."},
        {"resume_id": 2, "chunk_id": "r2_c3", "chunk_text": "Proficient in HTML, CSS, React, Redux, and Node.js."},
    ]

    EMBEDDING_DIM = 384
    dummy_embeddings = np.random.rand(len(dummy_resume_chunks), EMBEDDING_DIM).astype('float32')

    TEST_DIR = "faiss_test_data"
    os.makedirs(TEST_DIR, exist_ok=True)
    TEST_INDEX_PATH = os.path.join(TEST_DIR, "resume_index.faiss")
    TEST_METADATA_PATH = os.path.join(TEST_DIR, "resume_metadata.json")

    try:
        set_index_paths(TEST_INDEX_PATH, TEST_METADATA_PATH)
        print("\n--- Initializing FAISS Index ---")
        faiss_index = initialize_faiss_index(EMBEDDING_DIM)
        _faiss_index = faiss_index

        print("\n--- Adding Embeddings and Metadata ---")
        metadata_only = [{"resume_id": c["resume_id"], "chunk_id": c["chunk_id"], "chunk_text": c["chunk_text"]}
                         for c in dummy_resume_chunks]
        add_embeddings_to_index(dummy_embeddings, metadata_only)
        print(f"Current index total vectors: {faiss_index.ntotal}")
        print(f"Current metadata mapping size: {len(_metadata_mapping)}")

        print("\n--- Testing Persistence (Save/Load) ---")
        save_faiss_index_and_mapping(faiss_index, _metadata_mapping, TEST_INDEX_PATH, TEST_METADATA_PATH) # Explicit save
        _faiss_index = None
        _metadata_mapping = []

        loaded_index, loaded_metadata = load_faiss_index_and_mapping(TEST_INDEX_PATH, TEST_METADATA_PATH)
        assert loaded_index.ntotal == len(dummy_resume_chunks)
        assert len(loaded_metadata) == len(dummy_resume_chunks)
        print("Index and metadata successfully loaded and verified.")

        _faiss_index = loaded_index
        _metadata_mapping = loaded_metadata

        print("\n--- Searching Index ---")
        job_description_query = "Looking for a Python developer with AWS and Docker experience, capable of leading a team."
        dummy_query_embedding = np.random.rand(EMBEDDING_DIM).astype('float32')

        print(f"Searching for top 3 similar chunks for: '{job_description_query[:50]}...'")
        search_results = search_index(dummy_query_embedding, k=3)

        print("\n--- Search Results ---")
        for i, res in enumerate(search_results):
            print(f"Result {i+1} (Dist: {res.get('distance', 'N/A'):.4f}): Resume {res['resume_id']} - {res['chunk_text'][:70]}...")

        assert len(search_results) <= 3
        if search_results:
            assert 'chunk_text' in search_results[0]
            assert 'resume_id' in search_results[0]
            print("Search results verified.")

        print("\n--- Testing search with k > total ---")
        large_k_results = search_index(dummy_query_embedding, k=100)
        print(f"Retrieved {len(large_k_results)} results when k=100 (total elements {loaded_index.ntotal})")
        assert len(large_k_results) == loaded_index.ntotal


    except VectorStoreError as e:
        print(f"Vector Store Error: {e}")
    except ValueError as e:
        print(f"Input Validation Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("\n--- Cleaning up test data ---")
        if os.path.exists(TEST_DIR):
            import shutil
            shutil.rmtree(TEST_DIR)
            print(f"Removed test directory: {TEST_DIR}")
        _faiss_index = None
        _metadata_mapping = []