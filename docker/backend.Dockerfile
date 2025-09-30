# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies
# Copy requirements.txt from the project root (context: ../) into the container
RUN pip install --no-cache-dir --default-timeout=900 \
    fastapi \
    "uvicorn[standard]" \
    SQLAlchemy \
    pymysql \
    python-dotenv \
    pdfplumber \
    python-docx \
    langchain \
    sentence-transformers \
    faiss-cpu \
    google-generativeai \
    python-multipart \
    numpy

# Copy the backend application code from the 'backend/' directory in the project root
# into the '/app/backend/' directory in the container
COPY backend/ /app/backend/

# Expose the port on which the FastAPI application will run
EXPOSE 8000

# Define the command to run the application using Uvicorn
# 'backend.app.main:app' tells Uvicorn to look for 'app' in 'backend/app/main.py'
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]