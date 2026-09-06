from langchain_core.language_models import BaseChatModel

from LLM.config import settings


def get_llm(model: str | None = None, temperature: float = 0) -> BaseChatModel:
    """Return a chat model for the configured provider."""
    provider = settings.llm_provider.lower()
    model_name = model or settings.llm_model

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=settings.openai_api_key,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=model_name,
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")


def get_vision_llm(model: str | None = None) -> BaseChatModel:
    """Return the vision-capable model used for image understanding."""
    return get_llm(model=model or settings.llm_vision_model, temperature=0)
