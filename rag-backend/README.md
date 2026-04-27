# RAG Backend (FastAPI + FAISS)

Minimal, production-ready Retrieval-Augmented Generation backend with FastAPI, FAISS, and sentence-transformers. It supports document upload, chunking, embedding, retrieval, and a Gemini placeholder for grounded answers.

## Features

- Upload PDF or text files
- Chunking (~500 chars) with metadata
- Vector search via FAISS
- JSON document store for chunk text
- Grounded answers with strict prompt format
- Simple in-memory cache
- Render-friendly startup and filesystem persistence

## Project Structure

```
rag-backend/
  main.py
  routes/
    upload.py
    query.py
  services/
    embedding.py
    vector_store.py
    retrieval.py
    llm.py
  utils/
    chunking.py
  data/
    index.faiss
    docs.json
  frontend/
    index.html
    styles.css
    app.js
  requirements.txt
  .env
```

## Requirements

- Python 3.10+ recommended
- Dependencies in requirements.txt

## Setup

```bash
pip install -r requirements.txt
```

Create a .env file if needed:

```
GEMINI_API_KEY=
```

## Run

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

## API Endpoints

### POST /upload

- Accepts: PDF or text file
- Action: extracts text, chunks, embeds, stores in FAISS and docs.json

Example (curl):

```bash
curl -X POST "http://localhost:10000/upload" \
  -F "file=@./sample.pdf"
```

### POST /query

- Accepts: JSON {"query": "..."}
- Action: embeds query, retrieves top 3 chunks, generates answer

Example (curl):

```bash
curl -X POST "http://localhost:10000/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What does the document say about pricing?"}'
```

Response shape:

```
{
  "answer": "LLM response placeholder",
  "chunks": [
    {"id": 0, "text": "...", "source": "file.pdf", "score": 0.12}
  ]
}
```

## Storage and Persistence

- FAISS index: data/index.faiss
- Document store: data/docs.json
- Both are kept in sync. Startup will load existing data or create new files.

If the index and docs are out of sync, the app raises a runtime error.

## Frontend (Optional)

A simple frontend is in frontend/.

- Open frontend/index.html in a browser for local testing
- Set API_BASE in frontend/app.js if the backend runs on a different origin

## Deployment on Render

- Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

- Use a persistent disk if you want data/ to survive deploys
- The app uses only relative paths and stores data in data/

## Notes

- Gemini API integration is a placeholder in services/llm.py
- No external vector DBs or LangChain
