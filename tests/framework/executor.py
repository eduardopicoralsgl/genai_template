"""Execution engine for YAML-declared tests."""

from __future__ import annotations

import importlib
from typing import Any, Callable

from tests.framework.config_models import TestConfig


def import_callable(dotted_path: str) -> Any:
    """Import a callable from 'module.path:function_name' notation."""
    if ":" not in dotted_path:
        raise ValueError(f"Invalid callable path '{dotted_path}': expected 'module.path:name'")
    module_path, attr_name = dotted_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr_name)


def execute(config: TestConfig) -> dict[str, Any]:
    """Execute a test based on config and return the result dict."""
    mode = config.execution.mode

    if mode == "single_node":
        return _execute_single_node(config)
    elif mode == "full_graph":
        return _execute_full_graph(config)
    elif mode == "api":
        return _execute_api(config)
    else:
        raise ValueError(f"Unknown execution mode: {mode}")


def _execute_single_node(config: TestConfig) -> dict[str, Any]:
    assert config.execution.node is not None
    node_fn: Callable[..., Any] = import_callable(config.execution.node)
    state = dict(config.initial_state)
    result = node_fn(state)
    # Router nodes return strings, not dicts — wrap them
    if not isinstance(result, dict):
        return {"__return__": result}
    return result


def _execute_full_graph(config: TestConfig) -> dict[str, Any]:
    assert config.execution.graph is not None
    factory: Callable[..., Any] = import_callable(config.execution.graph)
    graph = factory()
    state = dict(config.initial_state)
    result: dict[str, Any] = graph.invoke(state)
    return result


def _execute_api(config: TestConfig) -> dict[str, Any]:
    from fastapi.testclient import TestClient

    assert config.execution.app is not None
    assert config.execution.method is not None
    assert config.execution.path is not None

    app = import_callable(config.execution.app)
    client = TestClient(app)

    method = config.execution.method.upper()
    path = config.execution.path
    body = config.initial_state or None

    if method == "GET":
        response = client.get(path)
    elif method == "POST":
        response = client.post(path, json=body)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    return {
        "status_code": response.status_code,
        "body": response.json(),
    }
