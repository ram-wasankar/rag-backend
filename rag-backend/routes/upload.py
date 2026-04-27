from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader

from services.embedding import embedding_service
from services.vector_store import vector_store
from utils.chunking import chunk_text

router = APIRouter()


def extract_text(filename: str, content_type: str | None, data: bytes) -> str:
    name = filename.lower()
    is_pdf = name.endswith(".pdf") or content_type == "application/pdf"
    is_text = name.endswith(".txt") or (content_type or "").startswith("text/")

    if is_pdf:
        reader = PdfReader(BytesIO(data))
        parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text:
                parts.append(page_text)
        return "\n".join(parts)

    if is_text:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="ignore")

    raise HTTPException(status_code=400, detail="Only PDF or text files are supported.")


@router.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        text = extract_text(file.filename, file.content_type, data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}") from exc

    chunks = chunk_text(text, chunk_size=500)
    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text found.")

    embeddings = embedding_service.embed_texts(chunks)
    vector_store.add_embeddings(embeddings, chunks, source=file.filename)

    return {"chunks_added": len(chunks), "source": file.filename}
