from typing import Any

from .graph import build_graph
# from .state import PipelineState

graph = build_graph()


def run_pipeline(input_data: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = graph.invoke({"input": input_data})

    return result


# def _build_initial_state(req: Any) -> PipelineState: ...
