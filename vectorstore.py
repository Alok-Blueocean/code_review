from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import hugging_face_api_key

persist_directory = "./chroma_db"

from huggingface_hub import login
embeddings = HuggingFaceEmbeddings(model_name = 'BAAI/bge-large-en')

chroma = Chroma(persist_directory=persist_directory,
                embedding_function=embeddings)
retriever = chroma.as_retriever()

sql_persist_directory = "./chroma_db_sql"


sql_chroma = Chroma(persist_directory=sql_persist_directory,
                embedding_function=embeddings)
sql_retriever = sql_chroma.as_retriever()  

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from states import MessageState

# ============================================================
# 1. RAG Prompt (Java Code Reviewer)
# ============================================================



# ============================================================
# 3. Simple RAG Prompt (no human_input)
# ============================================================

prompt_RAG_simple = """
You are an expert Java code reviewer and developer. I will provide you with a Java coding scenario,
including a potential issue and relevant context. Your task is to:

1. Analyze the provided scenario and identify the coding style problem.
2. Generate syntactically correct and improved Java code.
3. Provide a clear explanation of the problem and how your solution fixes it.

Scenario:
{question}

Chat history:
{chat_history}

Context:
{context}

Please provide the corrected code and explanation.
"""

prompt = ChatPromptTemplate.from_template(prompt_RAG_simple)
