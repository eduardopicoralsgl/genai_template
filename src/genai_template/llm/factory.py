from __future__ import annotations

import logging
from collections.abc import Mapping

from genai_template.core.config import Settings, get_settings
from genai_template.llm.base import ChatCompletionClient
from genai_template.llm.providers.anthropic import AnthropicChatClient
from genai_template.llm.providers.azure import AzureChatClient
from genai_template.llm.providers.gemini import GeminiChatClient
from genai_template.llm.providers.openai import OpenAIChatClient
from genai_template.llm.router import LLMRouter

logger = logging.getLogger(__name__)


_router: LLMRouter | None = None


def _build_clients(settings: Settings) -> dict[str, ChatCompletionClient]:
    clients: dict[str, ChatCompletionClient] = {}

    if settings.has_openai:
        try:
            clients["openai"] = OpenAIChatClient(api_key=settings.openai_api_key)
        except Exception:
            logger.debug("OpenAI client failed to initialize", exc_info=True)

    if settings.has_azure:
        try:
            assert settings.azure_openai_endpoint
            assert settings.azure_openai_api_key
            clients["azure_openai"] = AzureChatClient(
                endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
        except Exception:
            logger.debug("Azure OpenAI client failed to initialize", exc_info=True)

    if settings.has_anthropic:
        try:
            clients["anthropic"] = AnthropicChatClient(api_key=settings.anthropic_api_key)
        except Exception:
            logger.debug("Anthropic client failed to initialize", exc_info=True)

    if settings.has_gemini:
        try:
            clients["gemini"] = GeminiChatClient(
                api_key=None if settings.google_genai_use_vertexai else settings.gemini_api_key,
            )
        except Exception:
            logger.debug("Gemini client failed to initialize", exc_info=True)

    if not clients:
        raise RuntimeError(
            "No LLM providers configured. "
            "Set at least one provider key in .env (e.g. OPENAI_API_KEY)."
        )

    return clients


def configure_llm_router(
    *,
    default_provider: str | None = None,
    model_map: Mapping[str, str] | None = None,
    provider_map: Mapping[str, str] | None = None,
    extra_clients: Mapping[str, ChatCompletionClient] | None = None,
) -> LLMRouter:
    global _router

    settings = get_settings()

    if extra_clients:
        clients = dict(extra_clients)
    else:
        clients = _build_clients(settings)

    resolved_default_provider = default_provider or settings.default_provider

    if model_map is None:
        model_map = {
            "response": settings.default_model,
            "decision": settings.default_model,
        }
    provider_map = provider_map or {}

    _router = LLMRouter(
        clients=clients,
        model_map=model_map,
        provider_map=provider_map,
        default_provider=resolved_default_provider,
    )
    return _router


def is_router_configured() -> bool:
    return _router is not None


def get_llm_router() -> LLMRouter:
    if _router is None:
        raise RuntimeError("LLM router not configured. Call configure_llm_router() first.")
    return _router
