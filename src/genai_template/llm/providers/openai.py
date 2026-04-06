from __future__ import annotations

from typing import Any, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from genai_template.llm.base import ChatCompletionClient, LLMResponse
from genai_template.llm.message_thread import Messages


def _to_openai_messages(messages: Messages) -> list[ChatCompletionMessageParam]:
    # Convert provider-agnostic messages to OpenAI format
    out: list[ChatCompletionMessageParam] = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        name = m.get("name")

        msg: dict[str, Any] = {
            "role": role,
            "content": content,
        }
        if name is not None:
            msg["name"] = name

        out.append(cast(ChatCompletionMessageParam, msg))
    return out


class OpenAIChatClient(ChatCompletionClient):
    def __init__(self, api_key: str | None = None) -> None:
        self._client = OpenAI(api_key=api_key)

    @property
    def provider(self) -> str:
        return "openai"

    def chat_completion(
        self,
        messages: Messages,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        oa_messages = _to_openai_messages(messages)

        response = self._client.chat.completions.create(
            model=model,
            messages=oa_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Extract text
        text = ""
        try:
            text = response.choices[0].message.content or ""
        except Exception:
            text = ""

        # Usage (best-effort)
        usage: dict[str, Any] | None = None
        try:
            if response.usage is not None:
                usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
                    "completion_tokens": getattr(response.usage, "completion_tokens", None),
                    "total_tokens": getattr(response.usage, "total_tokens", None),
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
