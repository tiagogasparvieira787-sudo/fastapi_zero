#!/bin/sh

# Excuta as migrações do banco de dados
uv run alembic upgrade head

# Inicia a aplicação
uvicorn --host 0.0.0.0 --port 8000 fastapi_zero.app:app