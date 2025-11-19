from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

class MessageState(BaseModel):
    question: str = Field(..., description="The user's question or prompt")
    answer: Optional[str] = Field(None, description="The model's answer to the question")
    context: Optional[List[str]] = Field(None, description="Contextual information retrieved from the vector store")
    application: Optional[str] = Field(None, description="which application query belongs to")
    query_type: Optional[str] = Field(None, description="Wether it is asking for summary or asking a particular issue")
    summary: Optional[str] = Field(None,description="summerise the answer")
    query_type_score: Optional[float] = Field(None, description="Confidence score for query type classification")
    query_language: Optional[str] = Field(None, description="The programming language the query is about")
    query_language_score: Optional[float] = Field(None, description="Confidence score for query language classification")
    retry_count: int = 0
    max_retries: int = 3
    awaiting_clarify: bool = False
    clarify_prompt: Optional[str] = Field(None, description="Prompt to clarify user input if needed")
    top_score: Optional[float] = Field(None, description="Top score from retrieved documents")
    retrieved_docs: Optional[List[Dict[str, Any]]] = Field(None, description="Documents retrieved from the vector store")
    history: Optional[List[Dict[str, str]]] = Field([], description="Conversation history")
