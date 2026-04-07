"""LLM mock builder for YAML-declared tests.

Builds a mock function matching the call_llm_chat signature that routes
responses based on purpose/origin from the YAML config.
"""

from __future__ import annotations

from typing import Any

from genai_template.llm.message_thread import LLMMessage, Messages

from tests.framework.config_models import LLMMockConfig


def build_llm_mock(config: LLMMockConfig):  # noqa: ANN201
    """Return a function with the same signature as call_llm_chat."""

    def mock_call_llm_chat(
        messages: Messages,
        purpose: str,
        origin: str,
        *,
        model: str = "response",
        provider: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        max_retries: int = 3,
        backoff_seconds: float = 0.5,
        **kwargs: Any,
    ) -> tuple[str, Messages]:
        # Route: by_origin > by_purpose > default
        text = (
            config.by_origin.get(origin)
            or config.by_purpose.get(purpose)
            or config.default
            or "mock response"
        )
        assistant_msg: LLMMessage = {"role": "assistant", "content": text}
        messages_out: Messages = [*messages, assistant_msg]
        return text, messages_out

    return mock_call_llm_chat
