from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    project_name: str = "hlpr"
    env_file: Optional[str] = ".env"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
