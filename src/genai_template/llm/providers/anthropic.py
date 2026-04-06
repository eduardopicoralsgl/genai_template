from __future__ import annotations

from typing import Any, cast

import anthropic
from anthropic.types import MessageParam

from genai_template.llm.base import ChatCompletionClient, LLMResponse
from genai_template.llm.message_thread import Messages


# -------------------------
# Conversion helper
# -------------------------


def _to_anthropic_messages(messages: Messages) -> tuple[str | None, list[MessageParam]]:
    """
    Anthropic separates system from messages.
    """
    system: str | None = None
    out: list[MessageParam] = []

    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")

        if role == "system":
            # Anthropic expects a single system string
            system = content if system is None else f"{system}\n{content}"
        elif role in ("user", "assistant"):
            out.append(
                cast(
                    MessageParam,
                    {
                        "role": role,
                        "content": content,
                    },
                )
            )
        else:
            role = "user"
            out.append(
                cast(
                    MessageParam,
                    {
                        "role": role,
                        "content": content,
                    },
                )
            )

    return system, out


# -------------------------
# Client
# -------------------------


class AnthropicChatClient(ChatCompletionClient):
    def __init__(self, api_key: str | None = None) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)

    @property
    def provider(self) -> str:
        return "anthropic"

    def chat_completion(
        self,
        messages: Messages,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        system, anth_messages = _to_anthropic_messages(messages)

        create_kwargs: dict[str, Any] = {
            "model": model,
            "messages": anth_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
            **kwargs,
        }
        if system is not None:
            create_kwargs["system"] = system

        response = cast(Any, self._client.messages).create(**create_kwargs)

        # Extract text
        text = ""
        try:
            parts = response.content
            text = "".join(p.text for p in parts if getattr(p, "type", None) == "text")
        except Exception:
            text = ""

        text = text.strip()

        # Usage (Anthropic format differs)
        usage: dict[str, Any] | None = None
        try:
            if hasattr(response, "usage") and response.usage is not None:
                usage = {
                    "input_tokens": getattr(response.usage, "input_tokens", None),
                    "output_tokens": getattr(response.usage, "output_tokens", None),
                }
        except Exception:
            usage = None

        return {
            "text": text,
            "raw": cast(Any, response),
            "model": model,
            "provider": self.provider,
            "usage": usage,
        }
