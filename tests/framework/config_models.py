"""Pydantic models for YAML test configuration schema."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class FieldAssertion(BaseModel):
    path: str
    expected: Any = None
    contains: str | None = None
    not_empty: bool | None = None
    exists: bool | None = None
    regex: str | None = None
    length_gt: int | None = None
    length_lt: int | None = None


class CustomValidator(BaseModel):
    function: str
    args: dict[str, Any] = Field(default_factory=dict)


class AssertionsConfig(BaseModel):
    fields: list[FieldAssertion] = Field(default_factory=list)
    custom_validators: list[CustomValidator] = Field(default_factory=list)


class LLMMockConfig(BaseModel):
    default: str | None = None
    by_purpose: dict[str, str] = Field(default_factory=dict)
    by_origin: dict[str, str] = Field(default_factory=dict)


class ServiceMockConfig(BaseModel):
    target: str
    return_value: Any = None


class MocksConfig(BaseModel):
    llm: LLMMockConfig | None = None
    services: list[ServiceMockConfig] = Field(default_factory=list)


class ExecutionConfig(BaseModel):
    mode: Literal["single_node", "full_graph", "api"]
    node: str | None = None
    graph: str | None = None
    method: str | None = None
    path: str | None = None
    app: str | None = None

    @model_validator(mode="after")
    def validate_mode_fields(self) -> ExecutionConfig:
        if self.mode == "single_node" and not self.node:
            raise ValueError("single_node mode requires 'node' field")
        if self.mode == "full_graph" and not self.graph:
            self.graph = "genai_template.orchestration.graph:build_graph"
        if self.mode == "api":
            if not self.method:
                raise ValueError("api mode requires 'method' field")
            if not self.path:
                raise ValueError("api mode requires 'path' field")
            if not self.app:
                self.app = "genai_template.api.main:app"
        return self


class DatasetItem(BaseModel):
    input: dict[str, Any]
    expected: dict[str, Any] = Field(default_factory=dict)


class ScoringConfig(BaseModel):
    min_score: float = 0.8


class TestConfig(BaseModel):
    __test__ = False  # Prevent pytest from collecting this as a test class

    name: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    execution: ExecutionConfig
    initial_state: dict[str, Any] = Field(default_factory=dict)
    mocks: MocksConfig | None = None
    assertions: AssertionsConfig | None = None
    dataset: list[DatasetItem] | None = None
    scoring: ScoringConfig | None = None
    timeout: int = 60
