import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from fastapi_zero.routers import auth, todos, users
from fastapi_zero.schemas import MessageSchema

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title='API FastZero')
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
def read_root():
    return {'message': 'Olá Mundo'}
