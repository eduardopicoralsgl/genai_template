from fastapi import APIRouter

from typing import Any

from genai_template.api.schemas.run import RunRequest, RunResponse
from genai_template.orchestration.runtime import run_pipeline


router = APIRouter()


@router.post("/run", response_model=RunResponse)
def run(req: RunRequest) -> dict[str, Any]:
    return run_pipeline(req.model_dump())
