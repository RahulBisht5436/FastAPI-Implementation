from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Required: set PORTKEY_API_KEY in .env (see .env.example).
    portkey_api_key: str
    # Portkey integration slug from the dashboard, e.g. @my-provider.
    portkey_provider: str
    default_llm_model: str = "gpt-4o-mini"
    portkey_config_id: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
