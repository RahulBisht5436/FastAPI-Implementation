import httpx
from fastapi import APIRouter

from LLM.config import settings

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/models")
async def list_models():
    """Return configured defaults and selectable model options."""
    return {
        "provider": settings.llm_provider,
        "default_reasoning_model": settings.llm_model,
        "default_vision_model": settings.llm_vision_model,
        "reasoning_models": settings.available_reasoning_models,
        "vision_models": settings.available_vision_models,
    }


@router.get("/health")
async def llm_health():
    """Check connectivity to the active LLM provider."""
    if settings.llm_provider.lower() == "openai":
        return {
            "provider": "openai",
            "status": "configured" if settings.openai_api_key else "missing_api_key",
            "model": settings.llm_model,
        }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()
            tags = response.json().get("models", [])
            installed = [item.get("name") for item in tags if item.get("name")]

        return {
            "provider": "ollama",
            "status": "ok",
            "base_url": settings.ollama_base_url,
            "installed_models": installed,
            "default_reasoning_model": settings.llm_model,
            "default_vision_model": settings.llm_vision_model,
        }
    except Exception as exc:
        return {
            "provider": "ollama",
            "status": "unreachable",
            "base_url": settings.ollama_base_url,
            "detail": str(exc),
        }
