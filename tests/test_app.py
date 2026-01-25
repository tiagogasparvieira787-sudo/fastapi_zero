from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.app import app


def test_root_deve_retornar_ola_mundo():
    """
    Este teste tem 3 etapas (AAA)
    - A: Arrange - Arranja
    - A: Act - Executa a coisa
    - A: Assert - Garante que X é X
    """
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get('/')

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'mensagem': 'Olá Mundo'}
