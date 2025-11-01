print("--- [DEBUG] main.py file is being executed by Python interpreter. ---")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.database import create_tables
from backend.core import embedding_generator, vector_store, llm_evaluator
from backend.app.routers import resume, evaluation, auth
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
    # _MODIFIED_: Changed back to the specific origin for better security practice
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # _MODIFIED_: More explicit logging throughout startup
    print("\n--- [STARTUP] Application startup sequence initiated. ---")

    print("--- [STARTUP] Step 1/4: Initializing database tables... ---")
    create_tables()
    print("--- [STARTUP] Step 1/4: Database tables initialized. ---")

    print("--- [STARTUP] Step 2/4: Initializing sentence-transformer embedding model... ---")
    try:
        embedding_generator.initialize_embedding_model()
        print("--- [STARTUP] Step 2/4: Embedding model loaded successfully. ---")
    except Exception as e:
        print(f"--- [STARTUP] CRITICAL FAILURE in Step 2/4: Failed to load embedding model: {e} ---")
        # In a real app, you might want to exit here if the model is critical
        return

    embedding_dim = embedding_generator.get_embedding_dimension()
    if embedding_dim is None:
        raise RuntimeError("Embedding dimension could not be determined at startup.")

    print("--- [STARTUP] Step 3/4: Loading/initializing FAISS vector store... ---")
    vector_store.set_index_paths(FAISS_INDEX_FILE, FAISS_METADATA_FILE)
    try:
        loaded_index, loaded_metadata = vector_store.load_faiss_index_and_mapping(FAISS_INDEX_FILE, FAISS_METADATA_FILE)
        print(f"--- [STARTUP] Step 3/4: Existing FAISS index loaded with {loaded_index.ntotal} vectors. ---")
    except vector_store.VectorStoreError as e:
        print(f"--- [STARTUP] INFO: No existing FAISS index found ({e}). Initializing a new one. ---")
        new_index = vector_store.initialize_faiss_index(embedding_dim)
        vector_store._faiss_index = new_index
        vector_store._metadata_mapping = []
        print(f"--- [STARTUP] Step 3/4: New FAISS index initialized. ---")
    except Exception as e:
        print(f"--- [STARTUP] CRITICAL FAILURE in Step 3/4: Unexpected error during FAISS index setup: {e} ---")
        raise

    print("--- [STARTUP] Step 4/4: Initializing Deepseek LLM client... ---")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL")
    if not deepseek_api_key:
        print("--- [STARTUP] WARNING: DEEPSEEK_API_KEY is not set. LLM evaluation will fail. ---")
    else:
        try:
            llm_evaluator.initialize_deepseek_client(deepseek_api_key, base_url=deepseek_base_url if deepseek_base_url else "https://api.deepseek.com/v1")
            print("--- [STARTUP] Step 4/4: Deepseek LLM client initialized successfully. ---")
        except Exception as e:
            print(f"--- [STARTUP] CRITICAL FAILURE in Step 4/4: Failed to initialize Deepseek LLM client: {e} ---")
    
    print("--- [STARTUP] Application startup sequence complete. Ready to accept requests. ---\n")


app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(evaluation.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Semantic Profiler API!"}