from fastapi import FastAPI, HTTPException
from vectorstore import retriever,chroma
from chains import model_chain
from pydantic import BaseModel,Field
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str = Field(max_length=512, description="The query string to search for similar documents.")
    number_of_docs: Optional[int] = Field(default=5, ge=1, le=10, description="Number of similar documents to return.")

class ScoredDocument(BaseModel):
    document: str = Field(description="The retrieved document.")
    score: float = Field(description="The similarity score of the retrieved document.")

class QueryResponse(BaseModel):
    query: str = Field(description="The original query string.")
    results: List[ScoredDocument] = Field(description="List of similar documents with their scores.")

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/query")
async def get_similar_documents(query: QueryRequest):
    try:
        results = retriever.get_relevant_documents(query.query)
        return results
    except Exception as e:
        print(f"Error occurred while fetching similar documents: {e}")
        return []

@app.post("/query_with_similarity_scores")
async def get_similar_documents(query: QueryRequest):
    try:
        results = chroma.similarity_search_with_score(query.query, k=query.number_of_docs)
        scored_results = [ScoredDocument(document=doc.page_content, score=score) for doc, score in results]
        return QueryResponse(query=query.query, results=scored_results)
    
    except Exception as e:
        print(f"Error occurred while fetching similar documents: {e}")
        return []
    
@app.post("/llm")
async def get_llm_response(query: str):
    try:
        response = model_chain({"question": query})
        return response
    except Exception as e:
        print(f"Error occurred while getting LLM response: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")