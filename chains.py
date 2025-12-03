from langchain_groq import ChatGroq
from config import *
from prompts import prompt_llm_chain as prompt,  router_prompt
from vectorstore import retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from states import MessageState
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# -------------------------
# LLM
# -------------------------
print(groq_api_key)

model = ChatGroq(
    api_key=groq_api_key,
    model=model_id,
    max_tokens=1024,
)

# -------------------------
# MEMORY (Replaces ConversationBufferWindowMemory)
# -------------------------

def get_chat_memory(session_id: str):
    return ChatMessageHistory()

# -------------------------
# LLMChain Replacement
# -------------------------

# Prompt template must be ChatPromptTemplate in LC3
# prompt = ChatPromptTemplate.from_template(prompt_llm_chain)

llm_chain = prompt | model

model_chain = RunnableWithMessageHistory(
    llm_chain,
    get_chat_memory,
    input_messages_key="human_input",
    history_messages_key="chat_history",
)

# -------------------------
# Router Chain
# -------------------------

# router_prompt = ChatPromptTemplate.from_template(prompt_router)

router_chain = (
    router_prompt
    | model
    | PydanticOutputParser(pydantic_object=MessageState)
)

# -------------------------
# SQL Model Chain
# -------------------------

# sql_prompt = ChatPromptTemplate.from_template(prompt)

sql_chain_base = prompt | model

sql_model_chain = RunnableWithMessageHistory(
    sql_chain_base,
    get_chat_memory,
    input_messages_key="human_input",
    history_messages_key="chat_history",
)
