from collections.abc import Iterable, Sequence

from typing import Any, Literal, TypedDict, cast


# -------------------------
# Generic message types (provider-agnostic)
# -------------------------


class LLMMessage(TypedDict, total=False):
    role: Literal["system", "user", "assistant"]
    content: str
    name: str | None


Messages = Sequence[LLMMessage]
ChatMessage = dict[str, Any]


# -------------------------
# Thread helper
# -------------------------


class ChatMessageThread:
    def __init__(self, messages: Iterable[LLMMessage] | None = None) -> None:
        self._messages: list[LLMMessage] = list(messages) if messages is not None else []

    @classmethod
    def from_raw_thread(cls, raw: Sequence[LLMMessage]) -> "ChatMessageThread":
        # Already normalized to LLMMessage
        return cls(list(raw))

    def add_system(self, content: str) -> "ChatMessageThread":
        self._messages.append({"role": "system", "content": content})
        return self

    def add_user(self, content: str, name: str | None = None) -> "ChatMessageThread":
        msg: LLMMessage = {"role": "user", "content": content}
        if name is not None:
            msg["name"] = name
        self._messages.append(msg)
        return self

    def add_assistant(
        self,
        content: str,
        name: str | None = None,
    ) -> "ChatMessageThread":
        msg: LLMMessage = {"role": "assistant", "content": content}
        if name is not None:
            msg["name"] = name
        self._messages.append(msg)
        return self

    def extend(self, other: "ChatMessageThread") -> "ChatMessageThread":
        self._messages.extend(other._messages)
        return self

    def clone(self) -> "ChatMessageThread":
        return ChatMessageThread(self._messages)

    def to_messages(self) -> list[LLMMessage]:
        return list(self._messages)


# -------------------------
# Normalization helper
# -------------------------


def normalize_thread(raw_thread: Iterable[dict[str, Any]]) -> list[LLMMessage]:
    messages: list[LLMMessage] = []

    for msg in raw_thread:
        role_str = str(msg.get("role", "user"))
        content = str(msg.get("content", ""))

        if role_str not in ("system", "user", "assistant"):
            role_str = "user"

        role = cast(Literal["system", "user", "assistant"], role_str)

        messages.append(
            {
                "role": role,
                "content": content,
                "name": None,
            }
        )

    return messages
