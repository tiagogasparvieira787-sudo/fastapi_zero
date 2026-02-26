from contextlib import contextmanager
from datetime import datetime

import factory
import factory.fuzzy
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from fastapi_zero.app import app
from fastapi_zero.core.security import get_password_hash
from fastapi_zero.core.settings import Settings
from fastapi_zero.db.database import get_session
from fastapi_zero.db.models import Todo, TodoState, User, table_registry


@pytest_asyncio.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(model, time=datetime(2026, 1, 14)):

    def fake_time_created_at_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    def fake_time_updated_at_hook(mapper, connection, target):
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_created_at_hook)
    event.listen(model, 'before_update', fake_time_updated_at_hook)

    yield time

    event.remove(model, 'before_update', fake_time_updated_at_hook)
    event.remove(model, 'before_insert', fake_time_created_at_hook)


@pytest_asyncio.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):

    password = 'string'

    fake_user = UserFactory(password=get_password_hash(password))

    session.add(fake_user)
    await session.commit()
    await session.refresh(fake_user)

    fake_user._clean_password = password

    return fake_user


@pytest_asyncio.fixture
async def other_user(session: AsyncSession):

    password = 'string12'

    fake_user = UserFactory(password=get_password_hash(password))

    session.add(fake_user)
    await session.commit()
    await session.refresh(fake_user)

    fake_user._clean_password = password

    return fake_user


@pytest_asyncio.fixture
def token(client: TestClient, user: User):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user._clean_password,
        },
    )

    return response.json()['access_token']


@pytest_asyncio.fixture
def settings():
    settings = Settings()

    return settings


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text', max_nb_chars=100)
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1
