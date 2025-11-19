from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import PydanticOutputParser
from states import MessageState

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

# class RouterOutput(BaseModel):
#     application: str
#     query_type: str

router_prompt = """You are an expert router that can route the query to the correct application based on the question. You are supposed to do 2 types of classification.
1. Classify the application the query belongs to. The applications are:
- JPA
- SQL
2. Classify the type of query. The types are:
- Summary
- Individual Issue

Question: {question}

{format_instructions}
"""
prompt_router= PromptTemplate(template=router_prompt, 
                              input_variables = ["question"],
                              partial_variables={ "format_instructions": PydanticOutputParser(pydantic_object=MessageState).get_format_instructions()}
                              )

# model_with_structed_output = model.with_structured_output(RouterOutput)


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

{human_input}
Please provide the corrected code and a detailed explanation.
    """

prompt_llm_chain = PromptTemplate(
    input_variables=["question", "chat_history", "context","human_input"],
    template=prompt_RAG
)
