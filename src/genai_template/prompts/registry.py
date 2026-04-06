_FALLBACK_PROMPTS: dict[str, str] = {
    "example": "You are a helpful assistant. Answer the user's question concisely.",
}


def get_prompt(name: str) -> str:
    try:
        return fetch_from_registry(name)
    except Exception:
        return load_fallback(name)


def fetch_from_registry(name: str) -> str:
    # Replace with Langfuse prompt fetch or API call for your project.
    raise NotImplementedError


def load_fallback(name: str) -> str:
    return _FALLBACK_PROMPTS.get(name, "You are a helpful assistant.")
