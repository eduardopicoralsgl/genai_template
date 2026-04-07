"""Parametrized test runner for eval YAML configs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from tests.framework.config_loader import discover_configs
from tests.framework.config_models import FieldAssertion, TestConfig
from tests.framework.executor import execute
from tests.framework.field_checker import check_field

CONFIGS_DIR = Path(__file__).parent / "configs" / "eval"


def _collect() -> list[tuple[str, TestConfig]]:
    return discover_configs(CONFIGS_DIR) if CONFIGS_DIR.exists() else []


_cases = _collect()


def _score_result(result: dict[str, Any], expected: dict[str, Any]) -> float:
    """Score a single result against expected values. Returns 0.0-1.0."""
    if not expected:
        return 1.0

    checks: list[bool] = []
    for key, value in expected.items():
        if isinstance(value, dict):
            # Treat as assertion config (not_empty, contains, etc.)
            assertion = FieldAssertion(path=key, **value)
            passed, _ = check_field(result, assertion)
            checks.append(passed)
        else:
            # Exact match
            assertion = FieldAssertion(path=key, expected=value)
            passed, _ = check_field(result, assertion)
            checks.append(passed)

    return sum(1.0 for c in checks if c) / len(checks) if checks else 1.0


@pytest.mark.parametrize(
    ("test_id", "config"),
    _cases,
    ids=[c[0] for c in _cases],
)
def test_yaml_eval(test_id: str, config: TestConfig) -> None:
    assert config.dataset, f"Eval test '{test_id}' requires a dataset"

    scores: list[float] = []
    for item in config.dataset:
        # Build a copy of config with this dataset item's input
        item_config = config.model_copy(deep=True)
        item_config.initial_state = {"input": item.input}
        result = execute(item_config)
        score = _score_result(result, item.expected)
        scores.append(score)

    avg_score = sum(scores) / len(scores) if scores else 0.0
    min_score = config.scoring.min_score if config.scoring else 0.8
    assert avg_score >= min_score, f"Eval score {avg_score:.2f} < required {min_score}"
