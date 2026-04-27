import os


def generate_answer(context: str, query: str) -> str:
    """
    Integrate Gemini API here.
    DO NOT hardcode API key.
    Leave placeholder implementation.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = (
        "Context:\n{context}\n\n"
        "Question:\n{query}\n\n"
        "Answer ONLY from context.\n"
        'If not found, return "Not found".'
    ).format(context=context, query=query)

    _ = api_key
    _ = prompt
    return "LLM response placeholder"
