import logging
import re
import time

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.models.chat import ChatRequest, ChatResponse
from app.services import llm
from app.services.gemini import GeminiError
from app.services.search import search_chunks

router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Small talk that doesn't need a document search or a Gemini call.
_SMALL_TALK = re.compile(
    r"(hi+|hello+|hey+|yo|good (morning|afternoon|evening)|thanks?|thank you|thx|ok(ay)?|bye)[\s!.?]*",
    re.IGNORECASE,
)
_GREETING = "Hi! Ask me a question about your uploaded documents and I'll answer with the file and page."


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty.")
    if _SMALL_TALK.fullmatch(question):
        return ChatResponse(answer=_GREETING, sources=[])

    start = time.perf_counter()
    sources = search_chunks(question, body.top_k or get_settings().top_k)
    searched = time.perf_counter()
    if not sources:
        return ChatResponse(
            answer="There are no processed documents to search yet. Upload one first.", sources=[]
        )

    try:
        text = llm.answer(question, sources)
    except GeminiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        logger.info("chat: search %.2fs, gemini %.2fs", searched - start, time.perf_counter() - searched)
    return ChatResponse(answer=text, sources=sources)
