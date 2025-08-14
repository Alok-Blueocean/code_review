from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

persist_directory = "./chroma_db"

embeddings = HuggingFaceEmbeddings(model_name = 'BAAI/bge-large-en')

chroma = Chroma(persist_directory=persist_directory,
                embedding_function=embeddings)
retriever = chroma.as_retriever()
