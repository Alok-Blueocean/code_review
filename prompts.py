from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from states import MessageState


# ============================================================
# 1. RAG Prompt (Java Code Reviewer)
# ============================================================

prompt_RAG = """
You are an expert Java code reviewer and developer. I will provide you with a Java coding scenario, 
including a potential issue and relevant context. Your task is to:

1. Analyze the provided scenario and identify the coding style problem.
2. Generate syntactically correct and improved Java code that addresses the issue.
3. Provide a clear and concise explanation of the problem and how your solution corrects it, 
   referencing the provided context.

Scenario:
{question}

Chat history:
{chat_history}

Context:
{context}

{human_input}

Please provide the corrected code and a detailed explanation.
"""

prompt_llm_chain = ChatPromptTemplate.from_template(prompt_RAG)

# ============================================================
# 2. Router Prompt (Classification)
# ============================================================

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from states import MessageState

parser = PydanticOutputParser(pydantic_object=MessageState)



format_instructions = parser.get_format_instructions()

router_template = """
You are an expert router that routes the user query to the correct application
and determines the query type.

You must classify the query into:

1. Application:
- JPA
- SQL

2. Query type:
- Summary
- Individual Issue

Question:
{question}

{format_instructions}
"""

router_prompt = ChatPromptTemplate.from_template(router_template)




# router_prompt = ChatPromptTemplate.from_template(
#     router_template.replace(
#         "{format_instructions}",
#         PydanticOutputParser(pydantic_object=MessageState).get_format_instructions()
#     )
# )

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
