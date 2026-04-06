from __future__ import annotations

import asyncio
import time
from typing import Any

from genai_template.llm.factory import get_llm_router
from genai_template.llm.message_thread import LLMMessage, Messages
from genai_template.observability.langfuse import get_langfuse


def call_llm_chat(
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
    router = get_llm_router()
    resolved_provider = router.resolve_provider(model, provider)
    resolved_model = router.resolve_model(model)

    with get_langfuse().start_as_current_observation(
        as_type="generation",
        name=f"llm.{purpose}",
        model=resolved_model,
        input={
            "messages": messages,
            "temperature": temperature,
            "provider": resolved_provider,
            "max_tokens": max_tokens,
        },
        metadata={
            "origin": origin,
            "provider": resolved_provider,
        },
    ) as obs:
        last_err: Exception | None = None

        for attempt in range(1, max_retries + 1):
            try:
                response = router.chat_completion(
                    messages=messages,
                    model=model,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                text = response["text"]

                obs.update(
                    output={
                        "success": True,
                        "response": text,
                    },
                    metadata={
                        "attempts": attempt,
                        "provider": response["provider"],
                        "usage": response.get("usage"),
                    },
                )

                assistant_msg: LLMMessage = {
                    "role": "assistant",
                    "content": text,
                }
                messages_out: Messages = [*messages, assistant_msg]
                return text, messages_out

            except Exception as exc:
                last_err = exc
                if attempt < max_retries:
                    time.sleep(backoff_seconds * (2 ** (attempt - 1)))
                    continue

                obs.update(
                    output={"success": False},
                    metadata={
                        "error_type": type(exc).__name__,
                        "error_stage": "llm_call",
                        "error": str(exc)[:200],
                        "attempts": attempt,
                        "provider": resolved_provider,
                    },
                )

        raise RuntimeError(
            f"LLM call failed after {max_retries} attempts: {last_err}"
        ) from last_err


async def call_llm_chat_async(
    messages: Messages,
    purpose: str,
    origin: str,
    *,
    model: str = "decision",
    provider: str | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    max_retries: int = 3,
    backoff_seconds: float = 0.5,
    **kwargs: Any,
) -> tuple[str, Messages]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: call_llm_chat(
            messages,
            purpose=purpose,
            origin=origin,
            model=model,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            **kwargs,
        ),
    )
