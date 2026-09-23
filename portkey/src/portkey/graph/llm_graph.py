from typing import TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from portkey.config import get_settings


class GraphState(TypedDict):
    user_message: str
    llm_response: str


def _build_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        api_key=settings.portkey_api_key,
        base_url=PORTKEY_GATEWAY_URL,
        model=settings.default_llm_model,
        default_headers=createHeaders(
            api_key=settings.portkey_api_key,
            provider=settings.portkey_provider,
            config=settings.portkey_config_id
        ),
    )


def llm_node(state: GraphState) -> GraphState:
    llm = _build_llm()
    response = llm.invoke([HumanMessage(content=state["user_message"])])
    return {"llm_response": response.content}


def build_llm_graph():
    graph = StateGraph(GraphState)
    graph.add_node("llm", llm_node)
    graph.add_edge(START, "llm")
    graph.add_edge("llm", END)
    return graph.compile()


llm_graph = build_llm_graph()
