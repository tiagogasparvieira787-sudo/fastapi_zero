from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.models import User
from fastapi_zero.schemas import UserPublic


def test_root_deve_retornar_ola_mundo(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo'}


def test_create_user(client: TestClient):

    response = client.post(
        '/sign_up/',
        json={
            'username': 'alicerce',
            'email': 'test@example.com',
            'password': 'masqueiquo',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'email': 'test@example.com',
        'username': 'alicerce',
    }


def test_read_users(client: TestClient):

    response = client.get('/get_all_users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):

    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/get_all_users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client: TestClient, user: User):

    response = client.put(
        '/update_user/1',
        json={
            'username': 'Pablo',
            'email': 'random@example.com',
            'password': '1234',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'Pablo',
        'email': 'random@example.com',
    }


def test_update_integrity_error(client: TestClient, user: User):

    client.post(
        '/sign_up',
        json={
            'username': 'Pablito',
            'email': 'Pablito@example.com',
            'password': 'ultrasecret',
        },
    )

    response = client.put(
        f'/update_user/{user.id}',
        json={
            'username': 'Pablito',
            'email': 'john@example.com',
            'password': 'idk123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Username or Email already exists!'
    }


def test_delete_user(client: TestClient, user: User):

    response = client.delete('/delete_user/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
