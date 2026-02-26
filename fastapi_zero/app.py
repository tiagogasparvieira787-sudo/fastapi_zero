import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from fastapi_zero.core import auth
from fastapi_zero.routers import todos, users
from fastapi_zero.schemas.users import MessageSchema

if sys.platform == 'win32':  # pragma: no cover
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(
    title='API FastZero',
    openapi_tags=[
        {'name': 'auth', 'description': 'Login e refresh de token'},
        {'name': 'users', 'description': 'Gestão de utilizadores'},
        {'name': 'todos', 'description': 'Gestão de tarefas'},
    ],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
def read_root():
    return {'message': 'Olá Mundo'}
