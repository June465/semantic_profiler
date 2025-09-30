from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import create_tables
from backend.core import embedding_generator, vector_store, llm_evaluator
from backend.app.routers import resume, evaluation
import os

# Define paths for FAISS index and metadata persistence
FAISS_INDEX_DIR = "faiss_index_data"
FAISS_INDEX_FILE = os.path.join(FAISS_INDEX_DIR, "resume_index.faiss")
FAISS_METADATA_FILE = os.path.join(FAISS_INDEX_DIR, "resume_metadata.json")

# Create the FastAPI application instance
app = FastAPI(
    title="Semantic Profiler API",
    description="API for Retrieval-Augmented Semantic Profiling of Candidate Resumes",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Application startup event triggered.")

    create_tables()

    try:
        embedding_model = embedding_generator.initialize_embedding_model()
        print("Embedding model loaded successfully for application use.")
    except Exception as e:
        print(f"CRITICAL: Failed to load embedding model at startup: {e}")

    embedding_dim = embedding_generator.get_embedding_dimension()
    if embedding_dim is None:
        raise RuntimeError("Embedding dimension could not be determined at startup.")

    vector_store.set_index_paths(FAISS_INDEX_FILE, FAISS_METADATA_FILE)

    try:
        loaded_index, loaded_metadata = vector_store.load_faiss_index_and_mapping(FAISS_INDEX_FILE, FAISS_METADATA_FILE)
        print(f"Existing FAISS index loaded with {loaded_index.ntotal} vectors.")
    except vector_store.VectorStoreError as e:
        print(f"No existing FAISS index found or error loading: {e}. Initializing a new one.")
        new_index = vector_store.initialize_faiss_index(embedding_dim)
        vector_store._faiss_index = new_index
        vector_store._metadata_mapping = []
    except Exception as e:
        print(f"CRITICAL: Unexpected error during FAISS index loading/initialization: {e}")
        raise

    # Initialize Deepseek LLM client
    # The API key must be available in the environment (e.g., from .env file)
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL") # Optional: allow base URL to be configurable
    if not deepseek_api_key:
        print("WARNING: DEEPSEEK_API_KEY is not set. LLM evaluation will fail without it.")
    else:
        try:
            llm_evaluator.initialize_deepseek_client(deepseek_api_key, base_url=deepseek_base_url if deepseek_base_url else "https://api.deepseek.com/v1")
            print("Deepseek LLM client initialized for application use.")
        except Exception as e:
            print(f"CRITICAL: Failed to initialize Deepseek LLM client at startup: {e}")


app.include_router(resume.router)
app.include_router(evaluation.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Semantic Profiler API!"}