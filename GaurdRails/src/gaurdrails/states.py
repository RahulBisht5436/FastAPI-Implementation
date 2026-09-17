from typing import TypedDict

from langchain_core.messages import BaseMessage


class States(TypedDict, total=False):
    messages: list[BaseMessage]
    response: str
    metadata: dict
    history: list[str]
