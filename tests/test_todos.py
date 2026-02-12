from datetime import datetime
from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import Todo, User
from tests.conftest import TodoFactory


def test_create_todo(client: TestClient, token, mock_db_time):
    fixed_time = datetime(2026, 1, 14, 12, 0, 0)

    with mock_db_time(Todo, fixed_time):
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test todo',
                'description': 'Test todo description',
                'state': 'draft',
            },
        )

    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
        'created_at': '2026-01-14T12:00:00',
        'updated_at': '2026-01-14T12:00:00',
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    session: AsyncSession, client: TestClient, user: User, token
):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session: AsyncSession, user: User, client: TestClient, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, description='description')
    )
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?description=description',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, state='draft')
    )
    session.add_all(TodoFactory.create_batch(5, user_id=user.id, state='todo'))
    await session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_delete_todos(
    client: TestClient,
    user: User,
    session: AsyncSession,
    token: str,
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        'todos/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been delected successfully'
    }


@pytest.mark.asyncio
async def test_delete_todo_error(
    client: TestClient,
    session: AsyncSession,
    user: User,
    token: str,
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'todos/{todo.id + 1}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_delete_other_user_todo(
    client: TestClient,
    session: AsyncSession,
    other_user: User,
    token: str,
):
    todo_other_user = TodoFactory(user_id=other_user.id)
    session.add(todo_other_user)
    await session.commit()

    response = client.delete(
        f'todos/{todo_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_todo_patch(
    client: TestClient,
    user: User,
    token: str,
    session: AsyncSession,
    mock_db_time,
):
    with mock_db_time(Todo) as time_created:
        todo = TodoFactory(state='draft', user_id=user.id)

        session.add(todo)
        await session.commit()
        await session.refresh(todo)

    with mock_db_time(
        Todo, time=datetime(2026, 1, 14, 12, 30, 00)
    ) as time_updated:
        response = client.patch(
            f'todos/{todo.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'test123',
            },
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'title': 'test123',
        'description': todo.description,
        'state': 'draft',
        'created_at': time_created.isoformat(),
        'updated_at': time_updated.isoformat(),
    }


@pytest.mark.asyncio
async def test_todo_patch_error(
    client: TestClient,
    user: User,
    session: AsyncSession,
    token: str,
):
    todo_user = TodoFactory(user_id=user.id)
    session.add(todo_user)
    await session.commit()
    await session.refresh(todo_user)

    response = client.patch(
        f'todos/{todo_user.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
