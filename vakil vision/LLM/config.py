import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-r1:8b")
    llm_vision_model: str = os.getenv("LLM_VISION_MODEL", "llama3.2-vision")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")

    available_reasoning_models: list[str] = [
        "deepseek-r1:8b",
        "deepseek-r1:14b",
        "qwen2.5:7b",
        "gpt-4o-mini",
    ]
    available_vision_models: list[str] = [
        "llama3.2-vision",
        "llava",
        "qwen2.5vl",
    ]


settings = Settings()
