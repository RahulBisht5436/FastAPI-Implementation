import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from .states import States
from .gaurdRailService import build_guarded_llm

load_dotenv()



guarded_llm = build_guarded_llm()


def query_llm(state: States) -> dict:
    query = input("Enter a query: ")
    messages = state.get("messages", [])
    response = guarded_llm.invoke(messages + [HumanMessage(content=query)])
    print(f"\nAssistant: {response.content}\n")
    return {"messages": messages + [response], "response": response.content}


def should_continue(_state: States) -> str:
    nextquery = input("Want to continue? (y/n): ")
    return "end" if nextquery == "n" else "query_llm"
