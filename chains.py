from langchain.chains import ConversationalRetrievalChain,LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from config import *
# from config import groq_api_key, model_id
from prompts import prompt,prompt_llm_chain,prompt_router
from vectorstore import retriever
from langchain_core.output_parsers import PydanticOutputParser
from states import MessageState

# model = ChatGroq(api_key=groq_api_key,
#                  model=model_id,
#                  max_tokens=1024,
#                  )
# chat_memory = ConversationBufferWindowMemory(
#     memory_key="chat_history",
#     return_messages=True,
#     max_tokens=1024,
#     k=5,  # Number of past interactions to keep in memory
# )

# model_chain = ConversationalRetrievalChain.from_llm(
#     llm=model,
#     memory=chat_memory,
#     combine_docs_chain_kwargs={"prompt": prompt},
#     retriever=retriever
# )

print(groq_api_key)
model = ChatGroq(api_key=groq_api_key,
                 model=model_id,
                 max_tokens=1024,
                 )
chat_memory = ConversationBufferWindowMemory(
    input_key="human_input",
    memory_key="chat_history",
    return_messages=False,
    max_tokens=1024,
    k=5,  # Number of past interactions to keep in memory
)

model_chain = LLMChain(
    llm=model,
    memory=chat_memory,
    prompt=prompt_llm_chain,
    verbose=True
)
# q1 = "List all the issues with my JPA entity mapping"
# model_chain.invoke({
#     "human_input": "",
#     "question": "What is issue in having more number of constructors?", 
#     "context": "Issues with JPA entity mapping include improper use of annotations, lack of default constructors, and incorrect data types."
#     })

router_chain = LLMChain(llm=model, prompt=prompt_router,output_parser=PydanticOutputParser(pydantic_object=MessageState))

sql_chat_memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    return_messages=True,
    max_tokens=1024,
    k=5,  # Number of past interactions to keep in memory
)

# sql_model_chain = ConversationalRetrievalChain.from_llm(
#     llm=model,
#     memory=chat_memory,
#     combine_docs_chain_kwargs={"prompt": prompt},
#     retriever=sql_retriever
# )

sql_model_chain = LLMChain(
    llm=model,
    memory=sql_chat_memory,
    prompt=prompt_llm_chain,
    verbose=True
)
