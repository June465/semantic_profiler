import numpy as np
from typing import List, Union, Optional
from sentence_transformers import SentenceTransformer

_embedding_model: Optional[SentenceTransformer] = None
_embedding_dimension: Optional[int] = None

def initialize_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    global _embedding_model, _embedding_dimension
    if _embedding_model is None:
        try:
            print("\n--- [EMBEDDING MODEL] ---")
            print(f"--- [EMBEDDING MODEL] Attempting to load '{model_name}'. ---")
            print("--- [EMBEDDING MODEL] NOTE: This step will download ~230MB on the first run and may take several minutes. Please be patient. ---")
            
            _embedding_model = SentenceTransformer(model_name)
            _embedding_dimension = _embedding_model.get_sentence_embedding_dimension()

            print(f"--- [EMBEDDING MODEL] Successfully loaded. Embedding dimension: {_embedding_dimension}. ---")
            print("---\n")
        except Exception as e:
            print(f"--- [EMBEDDING MODEL] CRITICAL ERROR: Failed to load SentenceTransformer model '{model_name}': {e} ---")
            raise 
    return _embedding_model

def get_embedding_dimension() -> Optional[int]:

    if _embedding_dimension is None:
        try:
            initialize_embedding_model()
        except Exception:
            return None
    return _embedding_dimension


def get_embeddings(texts: Union[str, List[str]], model: SentenceTransformer) -> Union[np.ndarray, List[np.ndarray]]:
    if not texts:
        return [] if isinstance(texts, list) else np.array([])

    try:
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise

if __name__ == '__main__':
    print("--- Testing embedding_generator functions ---")

    sample_chunks = [
        "John Doe. Software Engineer. Experience: Led development of new features.",
        "Skills: Python, Java, AWS, Docker, Kubernetes. Education: B.S. Computer Science."
    ]

    try:
        embedding_model = initialize_embedding_model()
        embedding_dimension = get_embedding_dimension()
        print(f"Model loaded and dimension is {embedding_dimension}")

        embeddings = get_embeddings(sample_chunks, embedding_model)

        print(f"\nGenerated {len(embeddings)} embeddings.")
        print(f"Type of embeddings: {type(embeddings)}")
        print(f"Shape of first embedding: {embeddings[0].shape}")
        print(f"Embedding dimension (from model): {embedding_dimension}")

        for i, emb in enumerate(embeddings):
            assert emb.shape == (embedding_dimension,), \
                f"Mismatch in embedding shape for chunk {i}: {emb.shape} vs ({embedding_dimension},)"
            print(f"Chunk {i+1} embedding shape verified.")

        single_text = "This is a job description query."
        single_embedding = get_embeddings(single_text, embedding_model)
        print(f"\nGenerated single embedding. Shape: {single_embedding.shape}")
        assert single_embedding.shape == (embedding_dimension,), \
            f"Mismatch in single embedding shape: {single_embedding.shape} vs ({embedding_dimension},)"
        print("Single embedding shape verified.")

        print("\nTesting with empty input:")
        empty_list_embeddings = get_embeddings([], embedding_model)
        print(f"Embeddings for empty list: {empty_list_embeddings}, Type: {type(empty_list_embeddings)}")
        assert isinstance(empty_list_embeddings, list) and not empty_list_embeddings

        empty_string_embedding = get_embeddings("", embedding_model)
        print(f"Embedding for empty string: {empty_string_embedding}, Type: {type(empty_string_embedding)}")
        assert isinstance(empty_string_embedding, np.ndarray) and empty_string_embedding.size == 0

    except Exception as e:
        print(f"An error occurred during direct testing: {e}")