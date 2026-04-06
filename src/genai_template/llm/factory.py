from __future__ import annotations

import logging
import os
from collections.abc import Mapping

from genai_template.llm.base import ChatCompletionClient
from genai_template.llm.providers.anthropic import AnthropicChatClient
from genai_template.llm.providers.azure import AzureChatClient
from genai_template.llm.providers.gemini import GeminiChatClient
from genai_template.llm.providers.openai import OpenAIChatClient
from genai_template.llm.router import LLMRouter

logger = logging.getLogger(__name__)


_router: LLMRouter | None = None


def _build_openai() -> OpenAIChatClient:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    return OpenAIChatClient(api_key=api_key)


def _build_azure() -> AzureChatClient:
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not endpoint or not api_key or not api_version:
        raise RuntimeError("Azure OpenAI env vars missing")

    return AzureChatClient(
        endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
    )


def _build_anthropic() -> AnthropicChatClient:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return AnthropicChatClient(api_key=api_key)


def _build_gemini() -> GeminiChatClient:
    api_key = os.getenv("GEMINI_API_KEY")
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    if use_vertex:
        return GeminiChatClient(api_key=None)

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set (and not using Vertex AI)")

    return GeminiChatClient(api_key=api_key)


def _build_clients() -> dict[str, ChatCompletionClient]:
    clients: dict[str, ChatCompletionClient] = {}

    try:
        clients["openai"] = _build_openai()
    except Exception:
        logger.debug("OpenAI client not configured", exc_info=True)

    try:
        clients["azure_openai"] = _build_azure()
    except Exception:
        logger.debug("Azure OpenAI client not configured", exc_info=True)

    try:
        clients["anthropic"] = _build_anthropic()
    except Exception:
        logger.debug("Anthropic client not configured", exc_info=True)

    try:
        clients["gemini"] = _build_gemini()
    except Exception:
        logger.debug("Gemini client not configured", exc_info=True)

    if not clients:
        raise RuntimeError("No LLM providers could be configured from environment variables.")

    return clients


def configure_llm_router(
    *,
    default_provider: str | None = None,
    model_map: Mapping[str, str] | None = None,
    provider_map: Mapping[str, str] | None = None,
    extra_clients: Mapping[str, ChatCompletionClient] | None = None,
) -> LLMRouter:
    global _router

    if extra_clients:
        clients = dict(extra_clients)
    else:
        clients = _build_clients()
    resolved_default_provider = (
        default_provider
        if default_provider is not None
        else os.getenv("DEFAULT_PROVIDER", "openai")
    )
    if model_map is None:
        default_model = os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")
        model_map = {"response": default_model, "decision": default_model}
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
