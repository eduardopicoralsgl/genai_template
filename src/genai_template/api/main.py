from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI

from genai_template.api.routes import api_router
from genai_template.llm.factory import configure_llm_router, is_router_configured

load_dotenv()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    if not is_router_configured():
        configure_llm_router()
    yield


app = FastAPI(title="GenAI Template", version="0.1.0", lifespan=lifespan)

app.include_router(api_router)
