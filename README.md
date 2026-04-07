# GenAI Template

Production-ready template for new GenAI client projects.

Fork this repository when starting a new project. It gives you a working foundation with
LangGraph orchestration, multi-provider LLM support, Langfuse observability, and
all tooling (pytest, mypy, ruff, pre-commit) pre-configured.

---

## Quick start

```bash
# 1. Clone / fork
git clone <repo-url> my-project && cd my-project

# 2. Install dependencies (requires uv — https://docs.astral.sh/uv/)
make install

# 3. Create your .env from the example
cp .env.example .env
# Then fill in at least one LLM provider key (e.g. OPENAI_API_KEY)

# 4. Run the test suite (works without API keys — uses a fake LLM)
make test

# 5. Start the API
make run-api

# 6. Try the hello-world endpoint
curl -s http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?", "use_llm": true}' | python -m json.tool
```

---

## Architecture

```
HTTP request ─► FastAPI ─► LangGraph pipeline ─► nodes ─► response
                                │
                                ├── example_node   (preprocessing, always runs)
                                ├── router_node    (conditional: LLM or skip)
                                └── llm_node       (calls LLM via provider router)
```

### How the pipeline works

1. **`POST /run`** receives a `RunRequest` (message + use_llm flag)
2. **`run_pipeline()`** invokes the LangGraph graph with the input
3. **`example_node`** runs first — marks the state as `processed = True`
4. **`router_node`** checks `use_llm`: routes to `llm_node` or directly to END
5. **`llm_node`** fetches a system prompt from the registry, builds a message thread
   with the user's message, calls the LLM through the provider router, and stores
   the response in `state["result"]`

### LLM provider router

The `LLMRouter` decouples your application code from specific providers. You configure
abstract model names (e.g. `"response"`, `"decision"`) that map to concrete models
and providers:

```
call_llm_chat(messages, model="response")
       │
       ▼
   LLMRouter
       │ resolve model: "response" → "gpt-4.1-mini"
       │ resolve provider: → "openai"
       ▼
   OpenAIChatClient.chat_completion()
```

Supported providers out of the box:
- **OpenAI** — `OPENAI_API_KEY`
- **Azure OpenAI** — `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_API_VERSION`
- **Anthropic** — `ANTHROPIC_API_KEY`
- **Google Gemini** — `GEMINI_API_KEY` (or Vertex AI via `GOOGLE_GENAI_USE_VERTEXAI=true`)

Only providers with configured credentials are loaded. The router picks from whatever
is available.

### Observability with Langfuse

Tracing is opt-in. When `LANGFUSE_ENABLED=true` and Langfuse credentials are set,
every LLM call and pipeline node is traced automatically. When disabled, a no-op
implementation is used — zero overhead, no code changes needed.

### Prompt management

`prompts/registry.py` follows an external-first pattern:
1. Try fetching from an external registry (Langfuse prompt management, API, etc.)
2. Fall back to local prompts defined in `_FALLBACK_PROMPTS`

For new projects, start with the fallback dict and plug in the registry when ready.

---

## Project structure

```
src/genai_template/
├── api/                    # FastAPI app, routes, and request/response schemas
│   ├── main.py             # App entrypoint with lifespan (configures LLM router)
│   ├── routes/             # Route handlers (/health, /run)
│   └── schemas/            # Pydantic models for requests and responses
├── orchestration/          # LangGraph pipeline
│   ├── state.py            # PipelineState TypedDict — the graph's shared state
│   ├── graph.py            # Graph builder (nodes, edges, conditional routing)
│   ├── runtime.py          # run_pipeline() — single entry point to invoke the graph
│   └── nodes/              # Individual graph nodes (example, router, llm)
├── llm/                    # Provider-agnostic LLM layer
│   ├── base.py             # ChatCompletionClient protocol and LLMResponse type
│   ├── call.py             # call_llm_chat() with retry, tracing, and model resolution
│   ├── router.py           # LLMRouter — maps abstract models to providers
│   ├── factory.py          # Builds clients from env vars, creates the router
│   ├── message_thread.py   # ChatMessageThread builder and message normalization
│   └── providers/          # Per-provider implementations (openai, anthropic, gemini, azure)
├── prompts/                # Prompt registry with external-first + local fallback
├── observability/          # Langfuse integration with NoOp fallback
│   └── eval/               # Simple evaluation runner for dataset-based scoring
├── core/                   # Pydantic Settings, structured logging, context
├── domain/                 # Domain models (extend per project)
├── repositories/           # Persistence abstractions (extend per project)
└── utils/                  # Shared utilities (extend per project)

tests/
├── conftest.py             # Shared setup: fake LLM client, Langfuse disabled
├── framework/              # YAML test framework (config loader, executor, assertions, mocking)
├── configs/                # YAML test declarations (unit/, integration/, eval/)
├── test_yaml_unit.py       # Parametrized runner for unit YAML tests
├── test_yaml_integration.py # Parametrized runner for integration YAML tests
└── test_yaml_eval.py       # Parametrized runner for eval YAML tests
```

---

## Environment variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|---|---|---|
| `DEFAULT_MODEL` | No | Default model name (default: `gpt-4.1-mini`) |
| `DEFAULT_PROVIDER` | No | Default provider (default: `openai`) |
| `OPENAI_API_KEY` | At least one provider | OpenAI API key |
| `ANTHROPIC_API_KEY` | At least one provider | Anthropic API key |
| `GEMINI_API_KEY` | At least one provider | Google Gemini API key |
| `AZURE_OPENAI_*` | At least one provider | Azure OpenAI config |
| `LANGFUSE_ENABLED` | No | Enable Langfuse tracing (default: `false`) |
| `LANGFUSE_PUBLIC_KEY` | If Langfuse enabled | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | If Langfuse enabled | Langfuse secret key |
| `LANGFUSE_HOST` | No | Langfuse host (default: `https://cloud.langfuse.com`) |

---

## Developer workflow

### Make targets

```bash
make install      # Install all dependencies with uv
make lint         # Run ruff check + format
make typecheck    # Run mypy in strict mode
make test         # Run full test suite
make eval         # Run evaluation tests only
make all          # lint + typecheck + test
make run-api      # Start uvicorn with hot reload
```

### Pre-commit hooks

```bash
uv run pre-commit install   # Install hooks (one-time)
```

Every commit runs: **ruff** (lint + format) → **mypy** (type check) → **pytest** (tests).

### Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

---

## Testing strategy

Tests are declared as **YAML files** in `tests/configs/` and run via pytest parametrize:

- **`configs/unit/`** — Single-node tests (`execution.mode: single_node`)
- **`configs/integration/`** — Full graph + API endpoint tests (`mode: full_graph | api`)
- **`configs/eval/`** — Dataset-based quality scoring (`dataset` + `scoring`)

To add a new test, drop a `.yaml` file in the right directory — no Python code needed.
The YAML schema supports field assertions (exact match, contains, regex, length checks),
LLM mocking (by purpose/origin), and service mocking.

The test suite uses a `FakeChatClient` (defined in `conftest.py`) that returns
deterministic responses. No API keys or network access required.

---

## Adapting for a new project

After forking:

1. **Rename** the project in `pyproject.toml` and the `src/genai_template/` package
2. **Define your pipeline state** — edit `orchestration/state.py` with your domain fields
3. **Add nodes** — create new nodes in `orchestration/nodes/` for your business logic
4. **Wire the graph** — update `orchestration/graph.py` with your node topology
5. **Set up prompts** — add entries to `_FALLBACK_PROMPTS` in `prompts/registry.py`
   (or integrate with Langfuse prompt management)
6. **Add domain models** — define your data structures in `domain/`
7. **Add persistence** — implement repository interfaces in `repositories/`
8. **Expand tests** — add cases to each test category as your pipeline grows
9. **Configure providers** — fill in `.env` with the API keys you need

---

## Design principles

1. **LangGraph is the orchestration engine** — Control flow lives in the graph. Business
   logic lives in nodes. Don't mix them.
2. **Provider-agnostic LLM calls** — Application code uses abstract model names.
   Switching providers is a config change, not a code change.
3. **Prompts are external-first** — Start with local fallbacks, graduate to a managed
   registry (Langfuse, etc.) when ready.
4. **Observability is opt-in but built-in** — Tracing never blocks local development.
   Enable it when you need it.
5. **Typed state** — `PipelineState` is a TypedDict. Add fields deliberately.
6. **Tests run without credentials** — The fake LLM client ensures CI works everywhere.
