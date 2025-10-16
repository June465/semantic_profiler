# In docker/backend.Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# 1. Install PyTorch separately using the official CPU index URL.
# This ensures we get a compatible version (>= 2.1) without GPU dependencies.
RUN pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# 2. Copy only the requirements file first to leverage Docker's build cache.
# This layer will only be re-run if requirements.txt changes.
COPY backend/requirements.txt .

# 3. Install the rest of the dependencies from the requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the application code.
COPY backend/ /app/backend/

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]