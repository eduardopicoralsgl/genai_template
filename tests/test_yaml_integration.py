"""Parametrized test runner for integration YAML configs."""

from pathlib import Path
from unittest.mock import patch

import pytest

from tests.framework.config_loader import discover_configs
from tests.framework.config_models import TestConfig
from tests.framework.executor import execute
from tests.framework.field_checker import assert_all_fields
from tests.framework.llm_mocker import build_llm_mock
from tests.framework.service_mocker import apply_service_mocks

CONFIGS_DIR = Path(__file__).parent / "configs" / "integration"


def _collect() -> list[tuple[str, TestConfig]]:
    return discover_configs(CONFIGS_DIR) if CONFIGS_DIR.exists() else []


_cases = _collect()


@pytest.mark.parametrize(
    ("test_id", "config"),
    _cases,
    ids=[c[0] for c in _cases],
)
def test_yaml_integration(test_id: str, config: TestConfig) -> None:
    patches = []
    try:
        if config.mocks and config.mocks.llm:
            mock_fn = build_llm_mock(config.mocks.llm)
            # Patch both the definition site and the import site in llm_node
            for target in [
                "genai_template.llm.call.call_llm_chat",
                "genai_template.orchestration.nodes.llm_node.call_llm_chat",
            ]:
                p = patch(target, side_effect=mock_fn)
                p.start()
                patches.append(p)

        if config.mocks and config.mocks.services:
            patches.extend(apply_service_mocks(config.mocks.services))

        result = execute(config)

        if config.assertions and config.assertions.fields:
            assert_all_fields(result, config.assertions.fields)
    finally:
        for p in patches:
            p.stop()
