from typing import Annotated

from pydantic import BaseModel, Field

from fastapi_zero.db.models import TodoState


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
