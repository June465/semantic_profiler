# 🎯 Semantic Profiler

> **AI-Powered Resume Profiling & Candidate Evaluation** using Retrieval-Augmented Generation (RAG).

Semantic Profiler automates resume screening by analyzing candidate resumes against job descriptions using vector search, LLM scoring, explainable AI (XAI), and bias-awareness checks.

---

## ✨ Features

- **🧠 RAG Semantic Matching**: Deep semantic evaluation beyond simple keyword matching using FAISS vector search.
- **📊 Explainable AI (XAI)**: Detailed score breakdowns across Technical Match, Experience, and Soft Skills.
- **⚖️ Bias Detection**: Parallel evaluation on anonymized data to flag potential evaluation bias.
- **🏆 Candidate Ranking**: Automated percentile calculation and candidate comparison.
- **🔐 Secure Authentication**: Full JWT-based user authentication and protected routing.

---

## 🛠️ Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, CSS Modules |
| **Backend** | Python, FastAPI, SQLAlchemy, PyJWT |
| **AI / RAG** | Sentence Transformers, FAISS, LangChain, DeepSeek LLM |
| **Database** | MySQL 8.0 |
| **DevOps** | Docker, Docker Compose, Nginx |

---

## 🚀 Quick Start

### 1. Environment Setup
Create a `.env` file in the project root:
```env
DEEPSEEK_API_KEY="your_deepseek_api_key"
SECRET_KEY="your_random_jwt_secret_key"
```

### 2. Start Application
From the project root:
```bash
cd docker
docker-compose up --build -d
```
> App frontend will be available at **[http://localhost:5173](http://localhost:5173)** and backend API at **http://localhost:8000**.

### 3. Create Admin User
Initialize the default admin account (`admin` / `changeme`):
```bash
docker-compose exec backend python -m backend.utils.create_first_user
```

---

## 📁 Project Architecture

```
semantic_profiler/
├── backend/            # FastAPI REST API, database models & AI core
│   ├── app/            # API routes (auth, resume, evaluation)
│   ├── core/           # RAG pipeline, LLM evaluator, vector store, bias module
│   └── database/       # SQLAlchemy models & DB connection
├── frontend/           # React TypeScript UI
│   └── src/            # Pages (Dashboard, Upload, Login) & components
├── docker/             # Docker Compose & Dockerfiles
│   └── docker-compose.yml
└── uploaded_resumes/   # Storage for candidate resume uploads
```

---

## 🔌 Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticate user & receive JWT token |
| `POST` | `/resume/upload` | Upload resume files (`.pdf`, `.docx`) |
| `POST` | `/evaluation/evaluate` | Evaluate candidates against a job description |
| `GET` | `/evaluation/results/{id}` | Retrieve evaluation results and bias analysis |

---

## 🛑 Stopping the App

```bash
cd docker
docker-compose down       # Stop containers
docker-compose down -v    # Stop containers and reset database volume
```
