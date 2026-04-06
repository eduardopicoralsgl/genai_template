import os

from dotenv import load_dotenv

from genai_template.llm.base import ChatCompletionClient, LLMResponse
from genai_template.llm.factory import configure_llm_router
from genai_template.llm.message_thread import Messages

load_dotenv()

# Disable external services for tests
os.environ["LANGFUSE_ENABLED"] = "false"
# Clear provider keys so tests never hit real APIs
for key in [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "AZURE_OPENAI_API_KEY",
]:
    os.environ.pop(key, None)


class FakeChatClient(ChatCompletionClient):
    """Deterministic LLM client used by the test suite."""

    @property
    def provider(self) -> str:
        return "fake"

    def chat_completion(
        self,
        messages: Messages,
        *,
        model: str,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        last_user_msg = ""
        for m in messages:
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
        return {
            "text": f"Hello from fake LLM! You said: {last_user_msg}",
            "raw": None,
            "model": model,
            "provider": self.provider,
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }


configure_llm_router(
    default_provider="fake",
    model_map={"response": "fake-model", "decision": "fake-model"},
    provider_map={},
    extra_clients={"fake": FakeChatClient()},
)
