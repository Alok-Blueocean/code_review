from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas import QueryRequest, QueryResponse, ScoredDocument, LLMRequest
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService


def get_vector_service() -> VectorService:
    return VectorService()


def get_llm_service() -> LLMService:
    return LLMService()


api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}


@api_router.post("/query", response_model=List[str])
async def query_similar(request: QueryRequest, svc: VectorService = Depends(get_vector_service)):
    try:
        results = svc.retrieve_texts(request.query, request.number_of_docs)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/query_with_similarity_scores", response_model=QueryResponse)
async def query_with_scores(request: QueryRequest, svc: VectorService = Depends(get_vector_service)):
    try:
        scored = svc.retrieve_with_scores(request.query, request.number_of_docs)
        mapped = [ScoredDocument(document=item[0], score=item[1]) for item in scored]
        return QueryResponse(query=request.query, results=mapped)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/llm")
async def llm_answer(request: LLMRequest, llm: LLMService = Depends(get_llm_service)):
    try:
        return {"answer": llm.answer(request.question, request.context)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

