"""Centralized application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # App
    app_env: str = "local"
    log_level: str = "INFO"

    # LLM defaults
    default_model: str = "gpt-4.1-mini"
    default_provider: str = "openai"

    # OpenAI
    openai_api_key: str | None = None
    openai_org_id: str | None = None
    openai_project_id: str | None = None

    # Azure OpenAI
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment: str | None = None

    # Anthropic
    anthropic_api_key: str | None = None

    # Gemini
    gemini_api_key: str | None = None
    google_genai_use_vertexai: bool = False
    google_cloud_project: str | None = None
    google_cloud_location: str = "us-central1"
    google_application_credentials: str | None = None

    # Langfuse
    langfuse_enabled: bool = False
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    # Prompts
    prompt_registry_backend: str = "fallback"

    # Computed
    has_openai: bool = Field(default=False, exclude=True)
    has_azure: bool = Field(default=False, exclude=True)
    has_anthropic: bool = Field(default=False, exclude=True)
    has_gemini: bool = Field(default=False, exclude=True)

    @model_validator(mode="after")
    def _set_provider_flags(self) -> Settings:
        self.has_openai = bool(self.openai_api_key)
        self.has_azure = bool(
            self.azure_openai_endpoint
            and self.azure_openai_api_key
            and self.azure_openai_api_version
        )
        self.has_anthropic = bool(self.anthropic_api_key)
        self.has_gemini = bool(self.gemini_api_key or self.google_genai_use_vertexai)
        return self

    @property
    def has_any_provider(self) -> bool:
        return self.has_openai or self.has_azure or self.has_anthropic or self.has_gemini

    @property
    def has_langfuse(self) -> bool:
        return (
            self.langfuse_enabled
            and bool(self.langfuse_public_key)
            and bool(self.langfuse_secret_key)
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
