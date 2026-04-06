from typing import TypedDict, Optional, Any


class PipelineState(TypedDict, total=False):
    input: dict[str, Any]
    processed: bool
    result: Optional[str]
    error: Optional[str]
