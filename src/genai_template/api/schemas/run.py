from pydantic import BaseModel


# -------------------------
# Request / Response models
# -------------------------
class RunRequest(BaseModel):
    message: str
    use_llm: bool = True


class RunResponse(BaseModel):
    processed: bool | None = None
    result: str | None = None
    error: str | None = None
