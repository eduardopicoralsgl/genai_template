"""Generic service mocking from YAML config."""

from __future__ import annotations

from unittest.mock import patch, _patch

from tests.framework.config_models import ServiceMockConfig


def apply_service_mocks(configs: list[ServiceMockConfig]) -> list[_patch]:  # type: ignore[type-arg]
    """Start unittest.mock.patch for each service config. Returns patches to stop later."""
    patches: list[_patch] = []  # type: ignore[type-arg]
    for cfg in configs:
        p = patch(cfg.target, return_value=cfg.return_value)
        p.start()
        patches.append(p)
    return patches
