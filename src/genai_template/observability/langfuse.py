import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from langfuse import Langfuse, get_client

from genai_template.core.config import get_settings

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


def get_langfuse() -> Langfuse | NoOpLangfuse:
    settings = get_settings()

    if not settings.langfuse_enabled:
        return _NOOP

    if not settings.has_langfuse:
        logger.error(
            "Langfuse enabled but missing LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY "
            "-- falling back to NoOp"
        )
        return _NOOP

    try:
        return get_client()
    except Exception:
        logger.exception("langfuse.init_failed -- falling back to NoOp")
        return _NOOP


_NOOP = NoOpLangfuse()
