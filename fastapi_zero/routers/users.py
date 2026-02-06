from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    FilterPage,
    MessageSchema,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

AnnotatedSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def sign_up(user: UserSchema, session: AnnotatedSession):

    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists!',
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: AnnotatedSession,
    current_user: CurrentUser,
    filter_users: Annotated[FilterPage, Query()],
):
    users = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )
    return {'users': users}


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions!'
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            detail='Username or Email already exists!',
            status_code=HTTPStatus.CONFLICT,
        )


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageSchema,
)
async def delete_user(
    user_id: int,
    session: AnnotatedSession,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions!',
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
