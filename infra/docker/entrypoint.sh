#!/bin/sh
set -e

# Excuta as migrações do banco de dados
alembic upgrade head

# Inicia a aplicação
uvicorn --host 0.0.0.0 --port 8000 --workers 4 fastapi_zero.app:app