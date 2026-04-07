"""Parametrized test runner for unit YAML configs."""

from pathlib import Path

import pytest

from tests.framework.config_loader import discover_configs
from tests.framework.config_models import TestConfig
from tests.framework.executor import execute
from tests.framework.field_checker import assert_all_fields

CONFIGS_DIR = Path(__file__).parent / "configs" / "unit"


def _collect() -> list[tuple[str, TestConfig]]:
    return discover_configs(CONFIGS_DIR) if CONFIGS_DIR.exists() else []


_cases = _collect()


@pytest.mark.parametrize(
    ("test_id", "config"),
    _cases,
    ids=[c[0] for c in _cases],
)
def test_yaml_unit(test_id: str, config: TestConfig) -> None:
    result = execute(config)
    if config.assertions and config.assertions.fields:
        assert_all_fields(result, config.assertions.fields)
