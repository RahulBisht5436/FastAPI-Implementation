from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph

from .node import query_llm, should_continue
from .states import States

graph = StateGraph(States)

graph.add_node("query_llm", query_llm)
graph.add_edge(START, "query_llm")
graph.add_conditional_edges(
    "query_llm",
    should_continue,
    {
        "end": END,
        "query_llm": "query_llm",
    },
)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke(
        {
            "messages": [SystemMessage(content="You are a helpful assistant.")],
            "response": "",
            "metadata": {},
            "history": [],
        }
    )
    print(result)
