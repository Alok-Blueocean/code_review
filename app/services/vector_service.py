from typing import List, Tuple
from vectorstore import chroma


class VectorService:
    def retrieve_texts(self, query: str, k: int = 5) -> List[str]:
        results = chroma.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def retrieve_with_scores(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        results = chroma.similarity_search_with_score(query, k=k)
        return [(doc.page_content, score) for doc, score in results]

