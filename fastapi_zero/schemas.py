from pydantic import BaseModel, EmailStr


class MessageSchema(BaseModel):
    message: str


class UserPublic(BaseModel):
    username: str
    email: EmailStr


class UserSchema(UserPublic):
    password: str


class UserDB(UserPublic):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
