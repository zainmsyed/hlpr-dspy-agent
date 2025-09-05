from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    project_name: str = "hlpr"
    env_file: Optional[str] = ".env"
    debug: bool = True
    # Provider selection and API keys
    provider_name: Optional[str] = None  # e.g. "ollama", "openai", "anthropic", "google", "openrouter"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    provider_timeout: float = 10.0
    enable_training: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
