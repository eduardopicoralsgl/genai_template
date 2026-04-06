from __future__ import annotations

from typing import Protocol, runtime_checkable
from .message_thread import Messages
from typing import TypedDict, Any


class LLMResponse(TypedDict):
    text: str
    raw: Any
    model: str
    provider: str
    usage: dict[str, Any] | None


@runtime_checkable
class ChatCompletionClient(Protocol):
    @property
    def provider(self) -> str: ...

    def chat_completion(
        self,
        messages: Messages,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse: ...
