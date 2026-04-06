from ..state import PipelineState


def example_node(state: PipelineState) -> PipelineState:
    state["processed"] = True
    return state
