from __future__ import annotations

import os
from typing import Any, cast

from google import genai

from genai_template.llm.base import ChatCompletionClient, LLMResponse
from genai_template.llm.message_thread import Messages


# -------------------------
# Conversion helper
# -------------------------


def _to_gemini_parts(messages: Messages) -> tuple[str | None, list[dict[str, Any]]]:
    """
    Google Gen AI SDK expects:
    - optional system instruction (separate)
    - list of {role, parts}
    """
    system: str | None = None
    parts: list[dict[str, Any]] = []

    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")

        if role == "system":
            system = content if system is None else f"{system}\n{content}"
        else:
            gemini_role = "user" if role == "user" else "model"
            parts.append(
                {
                    "role": gemini_role,
                    "parts": [{"text": content}],
                }
            )

    return system, parts


# -------------------------
# Client
# -------------------------


class GeminiChatClient(ChatCompletionClient):
    def __init__(self, api_key: str | None = None) -> None:
        use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() in (
            "true",
            "1",
            "yes",
        )

        if use_vertex:
            project = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            self._client = genai.Client(
                vertexai=True,
                project=project,
                location=location,
            )
        else:
            resolved_api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not resolved_api_key:
                raise ValueError(
                    "Gemini API key not configured. Set GEMINI_API_KEY or GOOGLE_API_KEY."
                )
            self._client = genai.Client(api_key=resolved_api_key)

    @property
    def provider(self) -> str:
        return "gemini"

    def chat_completion(
        self,
        messages: Messages,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        system, gemini_messages = _to_gemini_parts(messages)

        config: dict[str, Any] = {
            "temperature": temperature,
            **({"max_output_tokens": max_tokens} if max_tokens is not None else {}),
            **kwargs,
        }
        if system is not None:
            config["system_instruction"] = system

        response = cast(Any, self._client.models).generate_content(
            model=model,
            contents=gemini_messages,
            config=config,
        )

        text = ""
        try:
            text = response.text or ""
        except Exception:
            text = ""

        text = text.strip()

        usage: dict[str, Any] | None = None
        try:
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = dict(response.usage_metadata)
        except Exception:
            usage = None

        return {
            "text": text,
            "raw": cast(Any, response),
            "model": model,
            "provider": self.provider,
            "usage": usage,
        }
