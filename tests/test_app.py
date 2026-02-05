from http import HTTPStatus

from fastapi.testclient import TestClient


def test_root_deve_retornar_ola_mundo(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo'}
