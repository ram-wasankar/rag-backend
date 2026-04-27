from fastapi import FastAPI
from dotenv import load_dotenv

from routes.upload import router as upload_router
from routes.query import router as query_router
from services.embedding import embedding_service
from services.vector_store import vector_store

load_dotenv()

app = FastAPI(title="RAG Backend")


@app.on_event("startup")
def on_startup() -> None:
    vector_store.initialize(embedding_service)


app.include_router(upload_router)
app.include_router(query_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
