from services.embedding import embedding_service
from services.vector_store import vector_store


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    embedding = embedding_service.embed_query(query)
    return vector_store.search(embedding, top_k=top_k)
