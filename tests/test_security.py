from http import HTTPStatus

from fastapi.testclient import TestClient
from jwt import decode

from fastapi_zero.models import User
from fastapi_zero.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():

    data = {'test': 'test'}

    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=ALGORITHM)

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client: TestClient, user: User):

    response = client.delete(
        '/delete_user/1', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_without_email(client: TestClient, user: User):

    token = create_access_token({'sub': ''})

    response = client.delete(
        '/delete_user/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_non_existent_user(client: TestClient, user: User):

    token = create_access_token({'sub': 'carlos@teste.com'})

    response = client.delete(
        '/delete_user/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
