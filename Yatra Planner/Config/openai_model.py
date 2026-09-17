import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

openai_model = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
)
