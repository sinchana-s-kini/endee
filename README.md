# 🚀 Endee AI Semantic Search & RAG System

## 📌 Project Overview

This project is a **production-style AI application** that demonstrates a **Semantic Search + Retrieval-Augmented Generation (RAG)** pipeline using the **Endee Vector Database**.

The system allows users to:

* Ingest custom knowledge
* Convert text into embeddings
* Store vectors in Endee
* Perform semantic search
* Generate AI-powered answers using retrieved context

This project showcases real-world AI infrastructure used in modern applications like ChatGPT, search engines, and enterprise knowledge systems.

---

## 🎯 Key Features

* ✅ Semantic Search using vector embeddings
* ✅ Endee Vector Database integration
* ✅ Text chunking for efficient retrieval
* ✅ RAG (Retrieval-Augmented Generation) pipeline
* ✅ AI-generated answers using Google Gemini
* ✅ FastAPI backend with REST APIs
* ✅ Interactive frontend (HTML, CSS, JS)
* ✅ Docker-ready architecture

---

## 🏗️ System Architecture

```
User Input (Frontend UI)
        ↓
FastAPI Backend (/api/search, /api/ingest)
        ↓
Sentence Transformer (Embeddings)
        ↓
Endee Vector Database (Storage & Retrieval)
        ↓
Retrieved Context
        ↓
Gemini API (Answer Generation)
        ↓
Final AI Response + Sources
```

---

## ⚙️ Tech Stack

| Layer      | Technology                               |
| ---------- | ---------------------------------------- |
| Backend    | FastAPI (Python)                         |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB  | Endee                                    |
| AI Model   | Google Gemini (gemma-3-1b-it)         |
| Frontend   | HTML, CSS, JavaScript                    |
| Deployment | Docker                                   |

---

## 🧠 How It Works

### 1. Knowledge Ingestion

* User inputs text via UI
* Text is split into smaller chunks
* Each chunk is converted into vector embeddings
* Stored in Endee with metadata

### 2. Semantic Search

* User query is converted into embedding
* Endee performs similarity search
* Top-K relevant chunks are retrieved

### 3. RAG Pipeline

* Retrieved chunks are combined as context
* Sent to Gemini API
* AI generates a contextual answer

---

## 📂 Project Structure

```
backend/
 ├── app.py              # FastAPI backend (API + RAG logic)
 ├── Dockerfile
 ├── requirements.txt

frontend/
 ├── index.html          # UI layout
 ├── script.js           # API calls
 ├── style.css           # Styling

endee-data/              # Vector storage (Endee data)
docker-compose.yml       # Container orchestration
README.md
```

---

## 🔌 API Endpoints

### 1. Ingest Data

```
POST /api/ingest/text
```

**Request Body:**

```json
{
  "title": "Sample Document",
  "text": "Your knowledge content here"
}
```

---

### 2. Semantic Search + AI Answer

```
POST /api/search
```

**Request Body:**

```json
{
  "query": "your question",
  "top_k": 5
}
```

---

### 3. Health Check

```
GET /api/health
```

---

## 🚀 Setup Instructions

### 🔹 Prerequisites

* Python 3.8+
* Docker & Docker Compose
* Git

---

### 🔹 Step 1: Clone Repository

```bash
git clone https://github.com/sinchana-s-kini/endee.git
cd endee
```

---

### 🔹 Step 2: Run Using Docker (Recommended)

```bash
docker-compose up --build
```

Access the app:

```
http://localhost:8000
```

---

### 🔹 Step 3: Run Without Docker (Optional)

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

---

## 🔑 Environment Variables

Set these if needed:

```bash
ENDEE_URL=http://localhost:8080/api/v1
GEMINI_API_KEY=your_api_key_here
```

---

## 🧪 Example Queries

After ingesting data, try:

* `who is Sinchana`
* `what is Vstand4U`


---

## 📈 Use Cases

* Personal knowledge assistant
* College event information system
* AI-powered FAQ system
* Document search engine
* Enterprise knowledge retrieval

---

## 🔥 Highlights

* Uses **Endee (mandatory requirement)**
* Implements **real RAG pipeline**
* Combines **AI + Backend + Frontend**
* Built with **production mindset**

---

## 📌 Future Improvements

* Chat-style interface (like ChatGPT)
* PDF / document ingestion
* Authentication system
* Deployment to cloud (AWS / Render)
* Streaming AI responses

---

## 👨‍💻 Author

**Sinchana**
Engineering Student | AI & Software Development Enthusiast

---

## ⭐ Acknowledgment

* Endee Vector Database (https://github.com/endee-io/endee)
* Sentence Transformers
* Google Gemini API

---

## 📎 Submission Note

This project was built as part of an AI/ML internship evaluation to demonstrate:

* Vector database usage
* Semantic search
* RAG-based AI system design
* Full-stack implementation

---
