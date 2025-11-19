from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

persist_directory = "./chroma_db"

from huggingface_hub import login
#login("")

embeddings = HuggingFaceEmbeddings(model_name = 'BAAI/bge-large-en')

chroma = Chroma(persist_directory=persist_directory,
                embedding_function=embeddings)
retriever = chroma.as_retriever()

sql_persist_directory = "./chroma_db_sql"


sql_chroma = Chroma(persist_directory=sql_persist_directory,
                embedding_function=embeddings)
sql_retriever = sql_chroma.as_retriever()  
