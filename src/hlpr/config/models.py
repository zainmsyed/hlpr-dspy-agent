from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic import ConfigDict


class ProviderType(str, Enum):
    LOCAL = "local"
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    GLM = "glm"
    COHERE = "cohere"
    MISTRAL = "mistral"


class OutputFormat(str, Enum):
    RICH = "rich"
    TXT = "txt"
    MD = "md"
    JSON = "json"


class UserConfiguration(BaseModel):
    default_provider: ProviderType = ProviderType.LOCAL
    default_format: OutputFormat = OutputFormat.RICH
    default_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    default_max_tokens: int = Field(default=8192, gt=0, le=32768)
    auto_save: bool = False
    default_output_directory: Path | None = None
    timeout_seconds: int | None = Field(default=30, ge=0)

    @field_validator("default_output_directory", mode="before")
    @classmethod
    def expand_path(cls, v):
        if v is None:
            return None
        return Path(v).expanduser().resolve()

    model_config = ConfigDict(use_enum_values=True)


class APICredentials(BaseModel):
    openai_api_key: str | None = None
    google_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    groq_api_key: str | None = None
    deepseek_api_key: str | None = None
    glm_api_key: str | None = None
    cohere_api_key: str | None = None
    mistral_api_key: str | None = None

    @field_validator("*", mode="before")
    @classmethod
    def _sanitize_api_key(cls, v):
        # Normalize API key strings: strip whitespace, reject newlines
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            # reject strings containing newlines (likely pasted wrong)
            if "\n" in v or "\r" in v:
                raise ValueError("API key contains invalid newline characters")
            if v == "":
                return None
            return v
        return v

    def get_key_for_provider(self, provider: ProviderType) -> str | None:
        mapping = {
            ProviderType.OPENAI: self.openai_api_key,
            ProviderType.GOOGLE: self.google_api_key,
            ProviderType.ANTHROPIC: self.anthropic_api_key,
            ProviderType.OPENROUTER: self.openrouter_api_key,
            ProviderType.GROQ: self.groq_api_key,
            ProviderType.DEEPSEEK: self.deepseek_api_key,
            ProviderType.GLM: self.glm_api_key,
            ProviderType.COHERE: self.cohere_api_key,
            ProviderType.MISTRAL: self.mistral_api_key,
        }
        if provider == ProviderType.LOCAL:
            return None
        return mapping.get(provider)


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


@dataclass
class ConfigurationPaths:
    config_dir: Path
    config_file: Path
    env_file: Path
    backup_dir: Path

    @classmethod
    def default(cls) -> ConfigurationPaths:
        config_dir = Path.home() / ".hlpr"
        return cls(
            config_dir=config_dir,
            config_file=config_dir / "config.yaml",
            env_file=config_dir / ".env",
            backup_dir=config_dir / "backups",
        )


class ConfigurationState(BaseModel):
    version: str = "1.0"
    config: UserConfiguration = Field(default_factory=UserConfiguration)
    credentials: APICredentials = Field(default_factory=APICredentials)

    model_config = ConfigDict(extra="forbid")

    def has_api_key_for_provider(self, provider: ProviderType) -> bool:
        if provider == ProviderType.LOCAL:
            return True
        return self.credentials.get_key_for_provider(provider) is not None
