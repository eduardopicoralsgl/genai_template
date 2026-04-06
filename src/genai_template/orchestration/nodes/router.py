from ..state import PipelineState


def router_node(state: PipelineState) -> str:
    if state.get("input", {}).get("use_llm"):
        return "llm"
    return "end"
