"""Dot-path field assertions for test result validation."""

from __future__ import annotations

import re
from typing import Any

from tests.framework.config_models import FieldAssertion


def resolve_path(data: Any, path: str) -> tuple[bool, Any]:
    """Resolve a dot-notation path into data. Returns (exists, value)."""
    parts = path.split(".")
    current = data
    for part in parts:
        # Handle integer indices: "items.0.name"
        if isinstance(current, (list, tuple)) and part.isdigit():
            idx = int(part)
            if idx < len(current):
                current = current[idx]
            else:
                return False, None
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return False, None
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            return False, None
    return True, current


def check_field(data: dict[str, Any], assertion: FieldAssertion) -> tuple[bool, str]:
    """Check one field assertion. Returns (passed, message)."""
    exists, value = resolve_path(data, assertion.path)

    if assertion.exists is not None:
        if assertion.exists and not exists:
            return False, f"{assertion.path}: expected to exist, but missing"
        if not assertion.exists and exists:
            return False, f"{assertion.path}: expected not to exist, but found {_short(value)}"
        if not assertion.exists and not exists:
            return True, f"{assertion.path}: correctly absent"

    if not exists and assertion.exists is None:
        # For other assertion types, the field must be resolvable
        return False, f"{assertion.path}: field not found"

    if assertion.expected is not None:
        if value == assertion.expected:
            return True, f"{assertion.path}: {_short(value)} == {assertion.expected}"
        return False, f"{assertion.path}: expected {assertion.expected}, got {_short(value)}"

    if assertion.contains is not None:
        val_str = str(value) if value is not None else ""
        if assertion.contains.lower() in val_str.lower():
            return True, f"{assertion.path}: contains '{assertion.contains}'"
        return False, f"{assertion.path}: '{assertion.contains}' not found in {_short(val_str)}"

    if assertion.not_empty is True:
        if value is None:
            return False, f"{assertion.path}: is None"
        if isinstance(value, (str, list, dict)) and len(value) == 0:
            return False, f"{assertion.path}: is empty"
        return True, f"{assertion.path}: not empty"

    if assertion.regex is not None:
        val_str = str(value) if value is not None else ""
        if re.search(assertion.regex, val_str):
            return True, f"{assertion.path}: matches regex '{assertion.regex}'"
        return False, f"{assertion.path}: does not match regex '{assertion.regex}'"

    if assertion.length_gt is not None:
        try:
            if len(value) > assertion.length_gt:
                return True, f"{assertion.path}: length {len(value)} > {assertion.length_gt}"
            return False, f"{assertion.path}: length {len(value)} not > {assertion.length_gt}"
        except TypeError:
            return False, f"{assertion.path}: cannot check length of {type(value).__name__}"

    if assertion.length_lt is not None:
        try:
            if len(value) < assertion.length_lt:
                return True, f"{assertion.path}: length {len(value)} < {assertion.length_lt}"
            return False, f"{assertion.path}: length {len(value)} not < {assertion.length_lt}"
        except TypeError:
            return False, f"{assertion.path}: cannot check length of {type(value).__name__}"

    return False, f"{assertion.path}: no assertion type specified"


def assert_all_fields(data: dict[str, Any], assertions: list[FieldAssertion]) -> None:
    """Run all field assertions. Raises AssertionError listing ALL failures."""
    failures: list[str] = []
    for assertion in assertions:
        passed, message = check_field(data, assertion)
        if not passed:
            failures.append(message)

    if failures:
        raise AssertionError(
            f"{len(failures)} assertion(s) failed:\n" + "\n".join(f"  - {f}" for f in failures)
        )


def _short(value: Any, limit: int = 100) -> str:
    s = str(value)
    return s[:limit] + "..." if len(s) > limit else s
