from __future__ import annotations

from typing import Any, cast

from openai.lib.azure import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam

from genai_template.llm.base import ChatCompletionClient, LLMResponse
from genai_template.llm.message_thread import Messages


def _to_azure_messages(messages: Messages) -> list[ChatCompletionMessageParam]:
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


class AzureChatClient(ChatCompletionClient):
    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        api_version: str,
    ) -> None:
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not configured.")
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not configured.")
        if not api_version:
            raise ValueError("AZURE_OPENAI_API_VERSION is not configured.")

        self._client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

    @property
    def provider(self) -> str:
        return "azure_openai"

    def chat_completion(
        self,
        messages: Messages,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        az_messages = _to_azure_messages(messages)

        response = self._client.chat.completions.create(
            model=model,
            messages=az_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        text = ""
        try:
            content = response.choices[0].message.content
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        except Exception:
            text = ""

        text = text.strip()

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
