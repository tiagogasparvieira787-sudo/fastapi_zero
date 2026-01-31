from http import HTTPStatus


def test_root_deve_retornar_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo'}


def test_create_user(client):

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
        'email': 'test@example.com',
        'username': 'alicerce',
    }


def test_get_all_users(client):

    response = client.get('/get_all_users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [{'username': 'alicerce', 'email': 'test@example.com'}]
    }


def test_update_user(client):

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
        'username': 'Pablo',
        'email': 'random@example.com',
    }


def test_delete_user(client):

    response = client.delete('/delete_user/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Pablo',
        'email': 'random@example.com',
    }
