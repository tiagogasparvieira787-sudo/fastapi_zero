FROM python:3.12-slim

ENV UV_PROJECT_ENVIRONMENT=.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .
RUN uv venv --clear .venv && uv pip install --python .venv/bin/python .
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD [ "./entrypoint.sh" ]
