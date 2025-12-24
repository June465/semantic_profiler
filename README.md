# Semantic Profiler

The Semantic Profiler is a full-stack web application designed to automate and enhance the recruitment process by providing AI-driven analysis of candidate resumes against specific job descriptions.

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Setup and Configuration](#setup-and-configuration)
- [Running the Application](#running-the-application)
- [Creating the First User](#creating-the-first-user)
- [Usage](#usage)
- [Stopping the Application](#stopping-the-application)

## Features

- **AI-Powered Semantic Analysis:** Uses a Retrieval-Augmented Generation (RAG) pipeline to provide nuanced, context-aware evaluations beyond simple keyword matching.
- **Explainable AI (XAI):** Delivers a detailed breakdown of scores across categories like Technical Match, Experience, and Soft Skills.
- **Bias-Aware Evaluation:** Performs a parallel evaluation on anonymized resume data to flag significant score discrepancies and alert recruiters to potential bias.
- **Comparative Analysis:** Calculates percentile rankings for each candidate within an evaluation batch, providing immediate context on their performance relative to the pool.
- **Secure Authentication:** All API endpoints are protected via JWT, with a complete login and protected route system.
- **Modern Tech Stack:** Built with FastAPI, React, and fully containerized with Docker for consistent and easy deployment.

## Technology Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** React, TypeScript, Vite, CSS Modules
- **Database:** MySQL
- **AI / ML:** `sentence-transformers`, `faiss-cpu`, `spacy`, `langchain`
- **DevOps:** Docker, Docker Compose, Nginx

## Prerequisites

- **Docker and Docker Compose:** The entire application runs in containers. You must have Docker Desktop (or Docker Engine with the Compose plugin) installed and running on your system.
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Git:** For cloning the repository.
- **Web Browser:** A modern web browser like Chrome, Firefox, or Edge.

## Setup and Configuration

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/semantic-profiler.git
    cd semantic-profiler
    ```

2.  **Configure Environment Variables:**
    The backend requires API keys and a secret key for security. Create a `.env` file in the **root directory** of the project (at the same level as the `backend` and `frontend` folders).

    ```bash
    # In /semantic-profiler/.env

    # Deepseek API Key (or other OpenAI-compatible API key)
    DEEPSEEK_API_KEY="your_api_key_here"

    # Key for JWT token encryption. Generate one with `openssl rand -hex 32`
    SECRET_KEY="your_random_32_byte_hex_string_here"
    ```
    Replace the placeholder values with your actual keys.

## Running the Application

The entire application stack (backend, frontend, and database) is managed by a single Docker Compose file.

1.  **Navigate to the `docker` Directory:**
    All commands should be run from within the `docker/` folder.
    ```bash
    cd docker
    ```

2.  **Build and Start the Containers:**
    This command will build the Docker images for the frontend and backend, download all dependencies, and start the services. The first build will take several minutes as it downloads AI models and dependencies.
    ```bash
    docker-compose up --build
    ```
    You will see logs from all three services (`mysql_db`, `fastapi_backend`, `static_frontend`). Wait until the logs stabilize and you see a message from the backend like:
    `INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`

## Creating the First User

Before you can use the application, you need to create an initial user account.

1.  **Open a NEW terminal window** (do not close the one running `docker-compose up`).

2.  **Navigate to the `docker` directory** in the new terminal.

3.  **Execute the User Creation Script:**
    This command runs the script inside the running `fastapi_backend` container.
    ```bash
    docker-compose exec backend python -m backend.utils.create_first_user
    ```
    You will see a success message confirming that the user `admin` has been created. The default password is `changeme`. You can change these credentials in the `backend/utils/create_first_user.py` file if you wish.

## Usage

1.  **Access the Application:**
    Open your web browser and navigate to:
    **[http://localhost:5173](http://localhost:5173)**

2.  **Log In:**
    You will be redirected to the login page. Use the credentials you just created:
    -   **Username:** `admin`
    -   **Password:** `changeme`

3.  **Start Evaluating:**
    -   Upload one or more resumes (`.pdf` or `.docx`).
    -   Enter a job title and description.
    -   Click "Evaluate Candidates" to get the AI-powered analysis.

## Stopping the Application

To stop all the running containers:
1.  Go to the terminal window where `docker-compose up` is running.
2.  Press **`Ctrl + C`**.
3.  To ensure all resources (including the network) are removed, run:
    ```bash
    docker-compose down
    ```
    To also remove the database volume (deleting all data), run:
    ```bash
    docker-compose down -v
    ```