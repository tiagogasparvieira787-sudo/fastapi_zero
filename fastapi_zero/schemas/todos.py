from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from fastapi_zero.db.models import TodoState


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
