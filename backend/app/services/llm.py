from google.genai import types

from app.core.config import get_settings
from app.models.chat import Source
from app.services import gemini

SYSTEM_PROMPT = """You answer questions about the user's uploaded documents.
Use only the numbered passages provided. If they don't contain the answer, say
"I don't know based on the provided documents."
Do not use outside knowledge. Be concise. When you state a fact, cite it like (filename, p. N)."""


def answer(question: str, sources: list[Source]) -> str:
    passages = "\n\n".join(
        f"[{i}] ({s.filename}, p. {s.page})\n{s.content}" for i, s in enumerate(sources, 1)
    )
    settings = get_settings()
    text = gemini.generate(
        [settings.gemini_model, settings.gemini_fallback_model],
        f"Passages:\n\n{passages}\n\nQuestion: {question}",
        types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.2),
    )
    if not text:
        raise gemini.GeminiError("Gemini returned an empty answer.")
    return text
