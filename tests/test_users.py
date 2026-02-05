from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.models import User
from fastapi_zero.schemas import UserPublic


def test_create_user(client: TestClient):

    response = client.post(
        '/users/',
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


def test_read_users(client: TestClient, user: User, token: str):

    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(
    client: TestClient,
    user: User,
    token: str,
):

    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
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


def test_update_integrity_error(
    client: TestClient,
    user: User,
    token: str,
):

    client.post(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Pablito',
            'email': 'Pablito@example.com',
            'password': 'ultrasecret',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Pablito',
            'email': 'john@example.com',
            'password': 'idk123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists!'}


def test_delete_user(
    client: TestClient,
    user: User,
    token: str,
):

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
