from langgrap.graph import StateGraph, START, END
from states import MessageState
from nodes import *
from langgraph.types import interrupt,Command
from langgraph.checkpoint.memory import InMemorySaver

#V2

graph = StateGraph(MessageState)

graph.add_node("get_request_type", get_request_type)

graph.add_node("clarify_query_type", clarify_query_type)

graph.add_node("clarify_query_language", clarify_query_language)

graph.add_node("get_request_language", get_request_language)

graph.add_node("jpa_node", jpa_node)
graph.add_node("fallback_node", fallback_node)

graph.add_node("sql_node", sql_node)
graph.add_node("score_check_node", score_check_node)
graph.add_node("clarify_node", clarify_node)



graph.add_edge(START,"get_request_type")

graph.add_conditional_edges(

"get_request_type",

route_query_node,

{



"clarify_query_type": "clarify_query_type",

"get_request_language": "get_request_language",

"awaiting": "clarify_query_type"

}

)

graph.add_edge(

"clarify_query_type",

"get_request_language"

)

graph.add_conditional_edges(

"get_request_language",

route_language_node,

{



"clarify_query_language": "clarify_query_language",

"awaiting": "clarify_query_language",

"score_check_node": "score_check_node",

}

)

graph.add_conditional_edges(
"clarify_query_language",
lambda state: "fallback_node" if state.query_language.lower() == "unknown" else "score_check_node",
{
"fallback_node": "fallback_node",
"score_check_node": "score_check_node",
}
)
graph.add_conditional_edges(
"score_check_node",
route_rag_score_node,
{
"JPA": "jpa_node",
"SQL": "sql_node",
"clarify": "clarify_node",
"Unknown": "fallback_node",
}
)
graph.add_edge("clarify_node", "score_check_node")

graph.add_edge("jpa_node", END)

graph.add_edge("sql_node", END)
graph.add_edge("fallback_node", END)

config = {"configurable":{"thread_id":"2"}}
app = graph.compile(checkpointer=InMemorySaver())

