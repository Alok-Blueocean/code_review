from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from states import MessageState
from chains import model, model_chain, sql_model_chain, router_chain
from vectorstore import chroma, sql_chroma
from prompts import format_instructions
from langgraph.types import Command, interrupt


SYSTEM_PROMPT = "Be concise and include examples when helpful."

def build_messages_from_history(state):
    print("[FUNC START] build_messages_from_history")
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for turn in state.history:
        role = turn.get("role")
        content = turn.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=state.question))
    print("[FUNC END] build_messages_from_history")
    return messages

def fallback_node(state: MessageState) -> MessageState:
    print("[FUNC START] fallback_node")
    if not state.history or state.history[-1].get("content") != state.question:
        state.history.append({"role":"user","content": state.question})

    messages = build_messages_from_history(state)
    response = model.invoke(messages)
    state.answer = response.content
    state.history.append({"role":"assistant","content": state.answer})
    print("[FUNC END] fallback_node")
    return state

def get_request_language(state: MessageState) -> MessageState:
    print("[FUNC START] get_request_language")
    parser = PydanticOutputParser(pydantic_object=MessageState)
    format_instructions = parser.get_format_instructions()

    prompt_text = """
    Return only valid json, no explaination, no extra text

    Classify the following question as either:
    - "JPA"
    - "SQL"
    - "unknown"

    Also provide a confidence score between 0 and 1.

    Question: {question}

    {format_instructions}
    """

    def escape_json(text: str) -> str:
        return text.replace("{", "{{").replace("}", "}}")


    prompt_template = ChatPromptTemplate.from_template(
    prompt_text.replace("{format_instructions}", escape_json(format_instructions))
)
    print("here1")
    chain = prompt_template | model | parser

    response = chain.invoke({"question": state.question,"format_instructions":format_instructions})

    state.query_type = response.query_type
    state.query_type_score = response.query_type_score
    state.query_language = response.query_language
    state.query_language_score = response.query_language_score
    print(f"[DEBUG] Determined query language: {state.query_language} with score: {state.query_language_score}")
    print("[FUNC END] get_request_language")
    return state

def clarify_query_language(state: MessageState) -> MessageState:
    print("[FUNC START] clarify_query_language")
    state.awaiting_clarify = True

    clarify_prompt = (
        "I couldn't determine whether your question is JPA or SQL. Could you please clarify?"
        "\nRespond with following options:\n- JPA\n- SQL"
    )
    state.clarify_prompt = clarify_prompt
    raw = interrupt(clarify_prompt)

    if state.retry_count >= state.max_retries:
        print("Maximum retries reached. Proceeding without clarification.")
        state.query_language = "unknown"
        state.awaiting_clarify = False
        print("[FUNC END] clarify_query_language")
        return state

    user_response = raw.strip().lower()
    if user_response == "jpa":
        state.query_language = "JPA"
    elif user_response == "sql":
        state.query_language = "SQL"
    else:
        print("I did not understand your response. Retrying...")
        if state.retry_count < state.max_retries:
            state.retry_count += 1
            state = clarify_query_language(state)
    state.awaiting_clarify = False
    print("[FUNC END] clarify_query_language")
    return state

def get_request_type(state: MessageState) -> MessageState:
    print("[FUNC START] get_request_type")
    parser = PydanticOutputParser(pydantic_object=MessageState)
    format_instructions = parser.get_format_instructions()

    prompt_text = """

    return only valid json, no explaination, no extra text

    Classify the following question as either:
    - "Summary"
    - "Individual Issue"
    - "Unknown"

    Also provide a confidence score 0–1.

    Question: {question}

    {format_instructions}
    """
    def escape_json(text: str) -> str:
        return text.replace("{", "{{").replace("}", "}}")


    prompt_template = ChatPromptTemplate.from_template(
    prompt_text.replace("{format_instructions}", escape_json(format_instructions))
)
    print("here1")
    chain = prompt_template | model | parser
    print("here2")
    response = chain.invoke({"question": state.question,"format_instructions":format_instructions})
    print("here3"+str(response))
    state.query_type = response.query_type
    state.query_type_score = response.query_type_score
    state.query_language = response.query_language
    state.query_language_score = response.query_language_score
    print("[FUNC END] get_request_type")
    return state

def clarify_query_type(state: MessageState) -> MessageState:
    print("[FUNC START] clarify_query_type")
    state.awaiting_clarify = True

    clarify_prompt = (
        "I couldn't determine whether your question is asking for a summary or a specific issue. "
        "Please clarify. Respond with following options:\n- Summary\n- Individual Issue"
    )
    state.clarify_prompt = clarify_prompt
    raw = interrupt(clarify_prompt)

    if state.retry_count >= state.max_retries:
        print("Maximum retries reached. Exiting clarification.")
        state.awaiting_clarify = False
        state.query_type = "Unknown"
        print("[FUNC END] clarify_query_type")
        return state

    user_response = raw.strip().lower()
    if user_response == "summary":
        state.query_type = "Summary"
    elif user_response == "individual issue":
        state.query_type = "Individual Issue"
    else:
        print("I did not understand your response. Retrying...")
        if state.retry_count < state.max_retries:
            state.retry_count += 1
            state = clarify_query_type(state)
    state.awaiting_clarify = False
    print("[FUNC END] clarify_query_type")
    return state

    
def route_query_node(state: MessageState) -> MessageState:
    if state.query_type_score is None or state.query_type_score < 0.9:
        return "clarify_query_type"
    if state.query_type_score is None or state.query_type_score >= 0.9:
        return "get_request_language"
    if state.awaiting_clarify:
        return "awaiting"
    else:
        return "fallback_node"

def route_language_node(state: MessageState) -> MessageState:
    if state.query_language_score is None or state.query_language_score < 0.9:
        return "clarify_query_language"
    if state.query_language_score is None or state.query_language_score >= 0.9:
        return "score_check_node"
    if state.awaiting_clarify:
        return "awaiting"
    else:
        return "fallback_node"
    
def router_node(state: MessageState) -> MessageState:
    # print(" Router Node "+str(state))
    response = router_chain.invoke({"question": state.question})
    # print(f"Router Response: {response}")
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
    state.answer = response.content
    # print(f"JPA Node Response: {state.answer}")
    return state
def sql_node(state: MessageState) -> MessageState:
    print("sql_node "+str(state))
    response = sql_model_chain.invoke({"question": state.question,"context": "/n/n".join(relevant_docs),"human_input":""})
    state.answer = response.content
    print(f"SQL Node Response: {state.answer}")
    return state

def route_rag_score_node(state: MessageState) -> MessageState:
    print("Route rag score")
    if state.top_score >= 0.3:
        print("Route rag score1")
        return state.query_language
    else:
        print("Route rag score2")
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
        # print(doc['content'])
    return scored_docs

def sql_query_retriever(question: str, k: int = 5):
    print(f"Querying retriever with question: {question}")
    docs = sql_chroma.similarity_search_with_score(question, k=k)
    print(f"Total documents retrieved: {len(docs)}")
    # print(docs)
    scored_docs = [{"content": doc.page_content, "score": score} for doc, score in docs[:k]]
    # print(f"Retrieved {len(scored_docs)} documents for question: {question}")
    for doc in scored_docs:
        print(f"Document score: {doc['score']:.3f}")
        print(doc['content'])
    return scored_docs

def score_check_node(state: MessageState):
    print("score_check_node "+str(state))
    if state.query_language == "JPA":
        docs = jpa_query_retriever(state.question, k=5)
    elif state.query_language == "SQL":
        docs = sql_query_retriever(state.question, k=5)
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
    # raw = input("User response: ")
    raw = interrupt(state.clarify_prompt)
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
