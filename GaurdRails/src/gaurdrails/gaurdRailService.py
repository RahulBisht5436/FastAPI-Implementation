from pathlib import Path
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

from nemoguardrails import RailsConfig
from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    streaming=True,
    api_key=os.getenv("OPENAI_API_KEY"),
)

NEMO_DIR = Path(__file__).parent / "nemo"

input_blocked_message = "I can't help with that request."
output_blocked_message = "I can't provide that information."

def build_guarded_llm() -> RunnableRails:
    config = RailsConfig.from_path(str(NEMO_DIR))
    return RunnableRails(
        config=config,
        llm=llm,
        passthrough=True,
        verbose=True,
        input_blocked_message=input_blocked_message,
        output_blocked_message=output_blocked_message,
    )