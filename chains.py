from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from config import *
from prompts import prompt
from vectorstore import retriever

model = ChatGroq(api_key=groq_api_key,
                 model=model_id,
                 max_tokens=1024,
                 )
chat_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    return_messages=True,
    max_tokens=1024,
    k=5,  # Number of past interactions to keep in memory
)

model_chain = ConversationalRetrievalChain.from_llm(
    llm=model,
    memory=chat_memory,
    combine_docs_chain_kwargs={"prompt": prompt},
    retriever=retriever
)
