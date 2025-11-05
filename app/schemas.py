from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    query: str = Field(max_length=512)
    number_of_docs: Optional[int] = Field(default=5, ge=1, le=10)


class ScoredDocument(BaseModel):
    document: str
    score: float


class QueryResponse(BaseModel):
    query: str
    results: List[ScoredDocument]


class LLMRequest(BaseModel):
    question: str
    context: Optional[str] = None

