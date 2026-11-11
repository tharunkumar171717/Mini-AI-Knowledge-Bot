from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=20)


class Source(BaseModel):
    filename: str
    page: int
    content: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
