import logging
import os
from contextlib import contextmanager
from typing import Any
from collections.abc import Generator

from langfuse import Langfuse, get_client

logger = logging.getLogger(__name__)


class NoOpObservation:
    def update(self, **kwargs: Any) -> None:
        pass


class NoOpLangfuse:
    @contextmanager
    def start_as_current_observation(self, **kwargs: Any) -> Generator[NoOpObservation, None, None]:
        yield NoOpObservation()

    def flush(self) -> None:
        pass

    def trace(self, **kwargs: Any) -> "NoOpLangfuse":
        return self

    def span(self, **kwargs: Any) -> NoOpObservation:
        return NoOpObservation()

    def generation(self, **kwargs: Any) -> NoOpObservation:
        return NoOpObservation()


def is_langfuse_enabled() -> bool:
    return os.getenv("LANGFUSE_ENABLED", "true").lower() in ("true", "1", "yes")


def _validate_langfuse_env() -> list[str]:
    required = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    return [k for k in required if not os.getenv(k)]


def get_langfuse() -> Langfuse | NoOpLangfuse:
    if not is_langfuse_enabled():
        return _NOOP

    missing = _validate_langfuse_env()
    if missing:
        logger.error(
            "Langfuse enabled but missing required env vars: %s — falling back to NoOp",
            ", ".join(missing),
        )
        return _NOOP

    try:
        return get_client()
    except Exception:
        logger.exception("langfuse.init_failed — falling back to NoOp")
        return _NOOP


_NOOP = NoOpLangfuse()
