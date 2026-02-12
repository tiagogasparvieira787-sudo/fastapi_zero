from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import Todo, User
from fastapi_zero.schemas import (
    FilterTodo,
    MessageSchema,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fastapi_zero.security import get_current_user

router = APIRouter(
    prefix='/todos', tags=['todos'], dependencies=[Depends(get_current_user)]
)

AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: AnnotatedSession,
):

    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def list_todos(
    user: CurrentUser,
    session: AnnotatedSession,
    filter_todos: Annotated[FilterTodo, Query()],
):

    query = select(Todo).where(Todo.user_id == user.id)

    if filter_todos.title:
        query = query.filter(Todo.title.contains(filter_todos.title))

    if filter_todos.description:
        query = query.filter(
            Todo.description.contains(filter_todos.description)
        )

    if filter_todos.state:
        query = query.filter(Todo.state == filter_todos.state)

    todos = await session.scalars(
        query.offset(filter_todos.offset).limit(filter_todos.limit)
    )

    return {'todos': todos.all()}


@router.delete(
    '/{todo_id}', status_code=HTTPStatus.OK, response_model=MessageSchema
)
async def delete_todo(
    todo_id: int, current_user: CurrentUser, session: AnnotatedSession
):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found'
        )

    await session.delete(todo)
    await session.commit()

    return {'message': 'Task has been delected successfully'}


@router.patch(
    '/{todo_id}', status_code=HTTPStatus.OK, response_model=TodoPublic
)
async def patch_todo(
    todo_id: int,
    todo: TodoUpdate,
    user: CurrentUser,
    session: AnnotatedSession,
):
    todo_db = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(todo_db, key, value)

    session.add(todo_db)
    await session.commit()
    await session.refresh(todo_db)

    return todo_db
