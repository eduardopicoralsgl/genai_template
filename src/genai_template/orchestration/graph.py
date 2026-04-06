from typing import Any
from langgraph.graph import END, StateGraph

from .state import PipelineState
from .nodes.example_node import example_node
from .nodes.llm_node import llm_node
from .nodes.router import router_node


def build_graph() -> Any:
    builder = StateGraph(PipelineState)

    builder.add_node("process", example_node)
    builder.add_node("llm", llm_node)

    builder.set_entry_point("process")

    builder.add_conditional_edges(
        "process",
        router_node,
        {
            "llm": "llm",
            "end": END,
        },
    )

    builder.add_edge("llm", END)

    return builder.compile()
