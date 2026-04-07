import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from genai_template.api.routes import api_router
from genai_template.core.config import get_settings
from genai_template.core.logging import setup_logging
from genai_template.llm.factory import configure_llm_router, is_router_configured

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(level=settings.log_level)

    if not is_router_configured():
        if not settings.has_any_provider:
            logger.error(
                "No LLM provider credentials found. "
                "Set at least one provider key in .env (e.g. OPENAI_API_KEY). "
                "The API will start but LLM calls will fail."
            )
        configure_llm_router()

    logger.info("GenAI Template API started (env=%s)", settings.app_env)
    yield
    logger.info("GenAI Template API shutting down")


app = FastAPI(title="GenAI Template", version="0.1.0", lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )


app.include_router(api_router)
