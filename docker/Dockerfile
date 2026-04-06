FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY src/ src/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "genai_template.api.main:app", "--host", "0.0.0.0", "--port", "8000"]