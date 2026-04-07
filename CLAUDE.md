# GenAI Template — Project Conventions

## What this is

A forkable template for GenAI client projects. Uses LangGraph for orchestration, a multi-provider LLM router, Langfuse for tracing, and FastAPI for the API layer.

## Architecture rules

- **Orchestration lives in LangGraph.** Control flow is in `orchestration/graph.py`. Business logic is in `orchestration/nodes/`. Don't mix them.
- **Nodes are pure functions.** Each node takes `PipelineState` and returns `PipelineState`. No side effects except LLM calls and logging.
- **Provider-agnostic LLM calls.** Application code uses abstract model names (`"response"`, `"decision"`). Never call a provider SDK directly from a node — always go through `call_llm_chat()`.
- **Prompts are external-first.** `prompts/registry.py` tries an external registry first, falls back to `_FALLBACK_PROMPTS`. Add prompts to the fallback dict during development, graduate to Langfuse prompt management later.
- **State is typed.** `PipelineState` is a TypedDict in `orchestration/state.py`. Add fields deliberately.
- **Observability is opt-in.** Langfuse tracing is always wired in but uses a NoOp when disabled. Never make tracing a hard dependency.

## Project structure

```
src/genai_template/
  api/              FastAPI app, routes, schemas
  core/             Settings (Pydantic), logging, context
  orchestration/    LangGraph graph, nodes, state, runtime
  llm/              Provider-agnostic LLM layer (router, call, providers/)
  prompts/          Prompt registry with fallback
  observability/    Langfuse integration, eval runner
  domain/           Domain models (extend per project)
  repositories/     Persistence abstractions (extend per project)
  utils/            Shared utilities (extend per project)
```

## Configuration

All config is in `core/config.py` via Pydantic Settings. Reads from `.env` automatically. Access via `get_settings()`. Never use `os.getenv()` directly in application code.

## Testing

Tests are declared as YAML files in `tests/configs/` (unit, integration, eval). Three thin pytest runners (`test_yaml_unit.py`, `test_yaml_integration.py`, `test_yaml_eval.py`) parametrize over them.

- **Unit YAMLs** test individual nodes: `execution.mode: single_node`
- **Integration YAMLs** test full graphs or API endpoints: `execution.mode: full_graph | api`
- **Eval YAMLs** score pipeline output against datasets: `dataset` + `scoring`

To add a test, drop a `.yaml` file in the right `tests/configs/` directory — no Python needed.

Tests always run without API keys. The `FakeChatClient` in `conftest.py` handles the default case. Integration tests with `mocks.llm` patch `call_llm_chat` with canned responses.

## Commands

```
make install      # uv sync
make lint         # ruff check + format
make typecheck    # mypy strict
make test         # pytest
make all          # lint + typecheck + test
make run-api      # uvicorn with hot reload
```

## Code style

- Python 3.13+, strict mypy, ruff with 100-char lines
- No docstrings on obvious functions. Comments only where logic isn't self-evident.
- Prefer explicit over clever. Prefer flat over nested.

## When adapting for a new project

1. Rename in `pyproject.toml` and `src/genai_template/`
2. Define pipeline state fields in `orchestration/state.py`
3. Add nodes in `orchestration/nodes/`, wire in `orchestration/graph.py`
4. Add prompts to `_FALLBACK_PROMPTS` in `prompts/registry.py`
5. Add domain models, repositories, and tests as needed
