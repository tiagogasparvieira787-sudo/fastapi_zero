from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DataError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import Todo, User
from tests.conftest import TodoFactory


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test', email='test@example.com', password='secret123'
        )

        session.add(new_user)
        await session.commit()

        user = await session.scalar(
            select(User).where(User.username == 'test')
        )

    assert asdict(user) == {
        'id': 1,
        'username': 'test',
        'email': 'test@example.com',
        'password': 'secret123',
        'todos': [],
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_enum_state_error(
    user: User, session: AsyncSession, mock_db_time
):
    with mock_db_time(model=Todo):
        todo = TodoFactory(user_id=user.id, state='not_found')
        session.add(todo)

        with pytest.raises(DataError):
            await session.commit()
