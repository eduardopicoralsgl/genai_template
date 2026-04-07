"""YAML test config discovery and loading."""

from __future__ import annotations

import warnings
from pathlib import Path

import yaml

from tests.framework.config_models import TestConfig


def load_test_config(path: Path) -> TestConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return TestConfig(**raw)


def discover_configs(directory: Path) -> list[tuple[str, TestConfig]]:
    """Return (test_id, config) pairs suitable for pytest.mark.parametrize."""
    if not directory.is_dir():
        return []

    results: list[tuple[str, TestConfig]] = []
    for yaml_file in sorted(directory.glob("*.yaml")):
        test_id = yaml_file.stem
        try:
            config = load_test_config(yaml_file)
            results.append((test_id, config))
        except Exception as exc:
            warnings.warn(f"Skipping invalid YAML {yaml_file}: {exc}", stacklevel=1)

    for yml_file in sorted(directory.glob("*.yml")):
        test_id = yml_file.stem
        try:
            config = load_test_config(yml_file)
            results.append((test_id, config))
        except Exception as exc:
            warnings.warn(f"Skipping invalid YAML {yml_file}: {exc}", stacklevel=1)

    return results
