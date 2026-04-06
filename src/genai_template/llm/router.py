from __future__ import annotations

from collections.abc import Mapping

from genai_template.llm.base import ChatCompletionClient, LLMResponse
from genai_template.llm.message_thread import Messages


class LLMRouter:
    def __init__(
        self,
        *,
        clients: Mapping[str, ChatCompletionClient],
        model_map: Mapping[str, str] | None = None,
        provider_map: Mapping[str, str] | None = None,
        default_provider: str = "openai",
    ) -> None:
        if not clients:
            raise ValueError("LLMRouter requires at least one client.")

        self._clients = dict(clients)
        self._model_map = dict(model_map or {})
        self._provider_map = dict(provider_map or {})
        self._default_provider = default_provider

        if self._default_provider not in self._clients:
            raise ValueError(f"Default provider '{self._default_provider}' is not configured.")

    def resolve_model(self, model: str) -> str:
        return self._model_map.get(model, model)

    def resolve_provider(self, model: str, provider: str | None = None) -> str:
        if provider is not None:
            if provider not in self._clients:
                raise ValueError(f"Provider '{provider}' is not configured.")
            return provider

        resolved_model = self.resolve_model(model)
        mapped_provider = self._provider_map.get(model) or self._provider_map.get(resolved_model)
        if mapped_provider is not None:
            if mapped_provider not in self._clients:
                raise ValueError(f"Provider '{mapped_provider}' is not configured.")
            return mapped_provider

        return self._default_provider

    def chat_completion(
        self,
        messages: Messages,
        *,
        model: str,
        provider: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        resolved_provider = self.resolve_provider(model, provider)
        resolved_model = self.resolve_model(model)
        client = self._clients[resolved_provider]
        return client.chat_completion(
            messages,
            model=resolved_model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
