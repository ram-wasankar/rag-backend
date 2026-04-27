import json
import threading
from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    def __init__(self, data_dir: Path = Path("data")) -> None:
        self.data_dir = data_dir
        self.index_path = self.data_dir / "index.faiss"
        self.docs_path = self.data_dir / "docs.json"
        self.index = None
        self.docs: list[dict] = []
        self.lock = threading.Lock()

    def initialize(self, embedding_service) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.docs = self._load_docs()

        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            dimension = embedding_service.dimension()
            self.index = faiss.IndexFlatL2(dimension)
            if self.docs:
                texts = [doc["text"] for doc in self.docs]
                embeddings = embedding_service.embed_texts(texts)
                self.index.add(embeddings)
            faiss.write_index(self.index, str(self.index_path))

        if self.index.ntotal != len(self.docs):
            raise RuntimeError(
                "FAISS index and docs.json are out of sync. "
                "Rebuild data or delete one of the files."
            )

    def _load_docs(self) -> list[dict]:
        if not self.docs_path.exists():
            self.docs_path.write_text("[]", encoding="utf-8")
            return []

        try:
            data = json.loads(self.docs_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError("docs.json contains invalid JSON.") from exc

        if not isinstance(data, list):
            raise RuntimeError("docs.json must be a JSON array.")

        return data

    def _save_docs(self) -> None:
        self.docs_path.write_text(
            json.dumps(self.docs, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

    def _save_index(self) -> None:
        faiss.write_index(self.index, str(self.index_path))

    def add_embeddings(self, embeddings: np.ndarray, texts: list[str], source: str) -> None:
        if self.index is None:
            raise RuntimeError("Vector store is not initialized.")

        if len(texts) != embeddings.shape[0]:
            raise ValueError("Embeddings and texts length mismatch.")

        embeddings = np.asarray(embeddings, dtype="float32")

        with self.lock:
            start_id = len(self.docs)
            new_docs = []
            for i, text in enumerate(texts):
                doc_id = start_id + i
                new_docs.append({"id": doc_id, "text": text, "source": source})

            self.index.add(embeddings)
            self.docs.extend(new_docs)
            self._save_docs()
            self._save_index()

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> list[dict]:
        if self.index is None:
            raise RuntimeError("Vector store is not initialized.")

        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray([query_embedding], dtype="float32")
        with self.lock:
            distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.docs):
                continue
            doc = self.docs[idx]
            results.append(
                {
                    "id": doc["id"],
                    "text": doc["text"],
                    "source": doc["source"],
                    "score": float(distance),
                }
            )

        return results


vector_store = VectorStore()
