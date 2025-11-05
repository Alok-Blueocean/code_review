from langchain.chains import LLMChain
from langchain_core.output_parsers import PydanticOutputParser

from langchain.schema import SystemMessage, HumanMessage, AIMessage
from states import MessageState
from langchain.prompts import PromptTemplate
from chains import model

SYSTEM_PROMPT = (
    "Be concise and include examples when helpful."
)

def build_messages_from_history(state):
    """
    Convert state.history into a list of langchain message objects.
    Expects state.history to be a list of dicts: {"role": "user"|"assistant", "content": "..."}
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # include prior turns
    for turn in state.history:
        role = turn.get("role")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        # optionally ignore system or other roles

    # append the current user question as the latest human message
    # Be careful not to duplicate: if you already appended the current question to history
    # earlier, skip this append. Here we assume you haven't appended yet.
    messages.append(HumanMessage(content=state.question))
    return messages

def fallback_node(state: MessageState) -> MessageState:
    # ensure current user message is recorded once in history (avoid double append)
    if not state.history or state.history[-1].get("content") != state.question:
        state.history.append({"role":"user","content": state.question})

    messages = build_messages_from_history(state)

    # call the ChatGroq model with the conversation messages
    response = model.invoke(messages)  # returns an AIMessage-like object
    state.answer = response.content

    # append assistant reply to history
    state.history.append({"role":"assistant","content": state.answer})
    return state


def get_request_language(state: MessageState) -> MessageState:
    """
    Determine the programming language of the request based on the user's question.
    """

    print("get request language ....."+str(state))
    print("2...........")
    parser = PydanticOutputParser(pydantic_object=MessageState)
    format_instructions = parser.get_format_instructions()
    print("Format instructions:"+str(format_instructions))
    prompt = """
    Classify the following question as either "JPA" if it is asking about Java code, "SQL" if it is asking about SQL code, or "unknown" if it is not clear.
    Also provide a confidence score between 0 and 1 for your classification.

    Please follow the JSON instructions exactly:
    Question: "{question}"

    {format_instructions}
    """
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template=prompt,
        partial_variables={"format_instructions": format_instructions}
    )
    # Simulate LLM response
    model.temperature = 0
    model.max_tokens = 800
    llm_chain = LLMChain(llm=model, prompt=prompt_template, 
                    output_parser=parser)
    response = llm_chain.invoke({"question": 
                                 state.question})
    state.query_type = response['text'].query_type
    state.query_type_score = response['text'].query_type_score
    state.query_language = response['text'].query_language
    state.query_language_score = response['text'].query_language_score
    print("Determined query language:", state.query_language, "with score:", state.query_language_score)
    return state

def clarify_query_language(state: MessageState) -> MessageState:
    """
    Clarify the query language if it is uncertain.
    """
    state.awaiting_clarify = True

    clarify_prompt = ("I couldn't determine whether your question is JPA or SQ. Could you please clarify?"
                      "Respond with following options:"
                      """- JPA
- SQL""")
    state.clarify_prompt = clarify_prompt
    # payload = {
    #     "prompt":clarify_prompt,
    #     "retry_count": state.retry_count,
    #     "max_retries": state.max_retries
    # }
    # print("Asking user for clarification:", clarify_prompt)
    raw = input("User response: ")
    # refined = interrupt(payload)
    # print(refined)
    # raw = refined.payload.get("user_response","")
    if state.retry_count >= state.max_retries:
        print("Maximum retries reached. Proceeding without clarification.")
        state.query_language = "unknown"
        state.awaiting_clarify = False
        return state
    user_response = raw.strip().lower()
    if user_response == "jpa":
        state.query_language = "JPA"
    elif user_response == "sql":
        state.query_language = "SQL"
    else:
        print("I did not understand your response. Please try again.")
        if state.retry_count < state.max_retries:
            state.retry_count += 1
            state = clarify_query_language(state)
    state.awaiting_clarify = False
    return state
    
from langchain.chains import LLMChain
from langchain_core.output_parsers import PydanticOutputParser
def get_request_type(state: MessageState) -> MessageState:
    """
    Determine the programming language of the request based on the user's question.
    """

    print("get request type ....."+str(state))
    parser = PydanticOutputParser(pydantic_object=MessageState)
    format_instructions = parser.get_format_instructions()
    print("Format instructions:"+str(format_instructions))
    prompt = """
    Classify the following question as either "Summary" if it is asking about Summary, "Individual Issue" if it is asking about a specific issue, or "unknown" if it is not clear.
    Also provide a confidence score between 0 and 1 for your classification.
    Question: "{question}"
    Follow the JSON instructions exactly:
    {format_instructions}
    """
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template=prompt,
        partial_variables={"format_instructions": format_instructions}
    )
    # Simulate LLM response
    llm_chain = LLMChain(llm=model, prompt=prompt_template, 
                    output_parser=parser)
    print("get request type 2"+str(state))
    response = llm_chain.invoke({"question": state.question})
    state.query_type = response['text'].query_type
    state.query_type_score = response['text'].query_type_score
    state.query_language = response['text'].query_language
    state.query_language_score = response['text'].query_language_score
    print("get request type final"+str(state))
    return state

def clarify_query_type(state: MessageState) -> MessageState:
    """
    Clarify the query language if it is uncertain.
    """
    print("clarify_query_type"+str(state))
    state.awaiting_clarify = True

    clarify_prompt = ("I couldn't determine whether your question is asking for a summary or a specific issue. Could you please clarify?"
                      "Respond with following options:"
                      """- Summary
- Individual Issue""")
    state.clarify_prompt = clarify_prompt
    print("Asking user for clarification:", clarify_prompt)
    raw = input("User response: ")
    # payload = {
    #     "prompt":clarify_prompt,
    #     "retry_count": state.retry_count,
    #     "max_retries": state.max_retries
    # }
    # refined = interrupt(payload)
    # print(refined)
    # raw = refined.payload.get("user_response","")
    if state.retry_count >= state.max_retries:
        print("Maximum retries reached. Exiting clarification.")
        state.awaiting_clarify = False
        state.query_type = "Unknown"
        return state
    user_response = raw.strip().lower()
    if user_response == "summary":
        state.query_type = "Summary"
    elif user_response == "individual issue":
        state.query_type = "Individual Issue"
    else:
        print("I did not understand your response. Please try again.")
        if state.retry_count < state.max_retries:
            state.retry_count += 1
            state = clarify_query_type(state)
    state.awaiting_clarify = False
    return state
    
def route_query_node(state: MessageState) -> MessageState:
    if state.query_type_score is None or state.query_type_score < 0.7:
        return "clarify_query_type"
    if state.query_type_score is None or state.query_type_score >= 0.7:
        return "get_request_language"
    if state.awaiting_clarify:
        return "awaiting"
    else:
        return "fallback_node"

def route_language_node(state: MessageState) -> MessageState:
    if state.query_language_score is None or state.query_language_score < 0.7:
        return "clarify_query_language"
    if state.query_language_score is None or state.query_language_score >= 0.7:
        return "score_check_node"
    if state.awaiting_clarify:
        return "awaiting"
    else:
        return "fallback_node"
    
def router_node(state: MessageState) -> MessageState:
    print(" Router Node "+str(state))
    response = router_chain.invoke({"question": state.question})
    print(f"Router Response: {response}")
    application = response['text'].application
    query_type = response['text'].query_type
    state.application = application
    state.query_type = query_type
    print(f"Routed to {application} and {query_type}")
    return state

def jpa_node(state: MessageState) -> MessageState:
    print("jpa_node "+str(state))
    relevant_docs = []
    for doc in state.retrieved_docs:
        relevant_docs.append(doc['content'])
    print(relevant_docs)
    response = model_chain.invoke({"question": state.question, 
                                   "context": "/n/n".join(relevant_docs),"human_input":""})
    print("Response from model_chain:"+str(response))
    state.answer = response['text']
    print(f"JPA Node Response: {state.answer}")
    return state
def sql_node(state: MessageState) -> MessageState:
    print("sql_node "+str(state))
    response = sql_model_chain.invoke({"question": state.question})
    state.answer = response['answer']
    print(f"SQL Node Response: {state.answer}")
    return state

def route_rag_score_node(state: MessageState) -> MessageState:
    if state.top_score >= 0.3:
        return state.query_language
    else:
        return "clarify"


def jpa_query_retriever(question: str, k: int = 5):
    print(f"Querying retriever with question: {question}")
    docs = chroma.similarity_search_with_score(question, k=k)
    print(f"Total documents retrieved: {len(docs)}")
    # print(docs)
    scored_docs = [{"content": doc.page_content, "score": score} for doc, score in docs[:k]]
    print(f"Retrieved {len(scored_docs)} documents for question: {question}")
    for doc in scored_docs:
        print(f"Document score: {doc['score']:.3f}")
        print(doc['content'])
    return scored_docs

def sql_query_retriever(question: str, k: int = 5):
    print(f"Querying retriever with question: {question}")
    docs = sql_chroma.similarity_search_with_score(question, k=k)
    print(f"Total documents retrieved: {len(docs)}")
    # print(docs)
    scored_docs = [{"content": doc.page_content, "score": score} for doc, score in docs[:k]]
    print(f"Retrieved {len(scored_docs)} documents for question: {question}")
    for doc in scored_docs:
        print(f"Document score: {doc['score']:.3f}")
        print(doc['content'])
    return scored_docs

def score_check_node(state: MessageState):
    print("score_check_node "+str(state))
    if state.query_language == "JPA":
        docs = jpa_query_retriever(state.question, k=5)
    elif state.query_language == "SQL":
        docs = jpa_query_retriever(state.question, k=5)
    else:
        docs = sql_query_retriever(state.question, k=5)
    state.retrieved_docs = docs
    state.top_score = docs[0]["score"] if docs else 0.0
    print(f"[score_check_node] question='{state.question}' top_score={state.top_score:.3f} retry={state.retry_count}")
    # thresholds
    return state

def clarify_node(state: MessageState):
    # If we're already awaiting clarify, nothing to do (frontend will prompt)
    if state.awaiting_clarify:
        return state
    # Build a short clarifying prompt
    state.clarify_prompt = (
        "I couldn't find a strong match in the knowledge base. "
        "Please rephrase your question or add details (error message, exact operation, versions).\n\n"
        "Examples:\n"
        " - 'Hibernate save() NullPointerException when entity is detached'\n"
        " - 'MySQL syntax error near ...'\n\n"
        "Please type your refined query:"
    )
    state.awaiting_clarify = True
    if state.retry_count >= state.max_retries:
        state.answer = "Maximum clarification attempts reached. Please try again later."
        state.awaiting_clarify = False
        return state
    print("[clarify_node] asking user for clarification (awaiting_clarify=True)"+str(state.clarify_prompt))
    raw = input("User response: ")
    # payload = {
    #     "prompt":state.clarify_prompt,
    #     "retry_count": state.retry_count,
    #     "max_retries": state.max_retries
    # }
    # refined = interrupt(payload)
    # print(refined)
    # raw = refined.payload.get("user_response","")
    user_response = raw.strip().lower()
    if user_response:
        state.question = user_response
        state.awaiting_clarify = False
        state.retry_count += 1
    return state