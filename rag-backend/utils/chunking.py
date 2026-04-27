def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    if not text:
        return []

    text = text.strip()
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end

    return chunks
