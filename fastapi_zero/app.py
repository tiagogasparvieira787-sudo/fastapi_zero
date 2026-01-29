from http import HTTPStatus

from fastapi import FastAPI

from fastapi_zero.schemas import MessageSchema

app = FastAPI(title='API FastZero')


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageSchema)
def read_root():
    return {'message': 'Olá Mundo'}
