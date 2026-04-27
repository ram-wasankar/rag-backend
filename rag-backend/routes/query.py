from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.llm import generate_answer
from services.retrieval import retrieve

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


RESPONSE_CACHE: dict[str, dict] = {}


@router.post("/query")
def query(payload: QueryRequest) -> dict:
    query_text = payload.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query is required.")

    cache_key = query_text.lower()
    cached = RESPONSE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    chunks = retrieve(query_text, top_k=3)
    if not chunks:
        response = {"answer": "Not found", "chunks": []}
        RESPONSE_CACHE[cache_key] = response
        return response

    context = "\n\n".join([chunk["text"] for chunk in chunks])
    answer = generate_answer(context, query_text)

    response = {"answer": answer, "chunks": chunks}
    RESPONSE_CACHE[cache_key] = response
    return response
