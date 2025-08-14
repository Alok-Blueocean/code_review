from langchain.prompts import PromptTemplate
prompt_RAG = """
    You are an expert Java code reviewer and developer. I will provide you with a Java coding scenario, including a potential issue and relevant context. Your task is to:

1.  Analyze the provided scenario and identify the coding style problem.
2.  Generate syntactically correct and improved Java code that addresses the issue.
3.  Provide a clear and concise explanation of the problem and how your solution corrects it, referencing the provided context.

Scenario:
{question}

Chat history
{chat_history}

Context:
{context}

Please provide the corrected code and a detailed explanation.
    """

prompt = PromptTemplate(
    input_variables=["question", "chat_history", "context"],
    template=prompt_RAG
)
