from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_zero.models import TodoState


class MessageSchema(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: Annotated[int, Field(ge=0)] = 0
    limit: Annotated[int, Field(ge=1)] = 10


class FilterTodo(FilterPage):
    title: Annotated[
        str | None, Field(default=None, min_length=3, max_length=20)
    ] = None
    description: Annotated[
        str | None, Field(default=None, min_length=5, max_length=30)
    ] = None
    state: TodoState | None = None


class TodoSchema(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=100)]
    description: Annotated[str, Field(min_length=1)]
    state: Annotated[TodoState, Field(description='Todo state')] = (
        TodoState.draft
    )


class TodoPublic(TodoSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class TodoList(BaseModel):
    todos: list[TodoPublic]


class TodoUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    description: Annotated[str | None, Field(min_length=1)] = None
    state: Annotated[
        TodoState | None,
        Field(description='Todo state', default=TodoState.draft),
    ] = None
