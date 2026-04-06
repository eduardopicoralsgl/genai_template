install:
	uv sync --all-extras

lint:
	uv run ruff check .
	uv run ruff format .

typecheck:
	uv run mypy --explicit-package-bases src/

test:
	uv run pytest -v

eval:
	uv run pytest tests/eval -v

all: lint typecheck test

run-api:
	uv run uvicorn genai_template.api.main:app --reload