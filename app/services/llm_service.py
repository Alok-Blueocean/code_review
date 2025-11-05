from typing import Optional
from chains import model_chain


class LLMService:
    def answer(self, question: str, context: Optional[str] = None) -> str:
        payload = {"question": question, "context": context or "", "human_input": ""}
        response = model_chain.invoke(payload)
        # model_chain returns dict-like with 'text'
        return response.get("text") if isinstance(response, dict) else str(response)

