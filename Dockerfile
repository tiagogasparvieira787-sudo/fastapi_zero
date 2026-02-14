FROM python:3.12-slim

ENV UV_PROJECT_ENVIRONMENT=.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .
RUN uv venv --clear .venv && uv pip install --python .venv/bin/python .

EXPOSE 8000
