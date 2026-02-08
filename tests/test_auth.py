from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from fastapi_zero.models import User


def test_get_token(client: TestClient, user: User):

    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user._clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert token['token_type'] == 'Bearer'
    assert 'access_token' in token


def test_token_wrong_password(client: TestClient, user: User):

    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'wrong_password',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password!'}


def test_token_inexistent_user(client: TestClient):

    response = client.post(
        '/auth/token',
        data={'username': 'no_user@no_domain.non', 'password': 'test'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password!'}


def test_token_expired_after_time(client: TestClient, user: User):
    with freeze_time('2026-01-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user._clean_password},
        )
        assert response.status_code == HTTPStatus.CREATED
        token = response.json()['access_token']

    with freeze_time('2026-01-14 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'lolol',
                'email': 'lol@test.com',
                'password': 'ultrasecret',
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_expired_after_time_in_refresh_token(
        client: TestClient, user: User
    ):
    with freeze_time('2026-01-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user._clean_password},
        )
        assert response.status_code == HTTPStatus.CREATED
        token = response.json()['access_token']

    with freeze_time('2026-01-14 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client: TestClient, user: User, token: str):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'
