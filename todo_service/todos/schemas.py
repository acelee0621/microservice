from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool


class TodoBase(BaseModel):
    title: str
    description: str | None = None


class TodoCreate(TodoBase):
    list_id: int


class TodoUpdate(BaseModel):  # 继承 BaseModel 避免继承 title
    title: str | None = None
    description: str | None = None
    completed: bool | None = None  # 避免默认 False


class TodoResponse(TodoBase):
    id: int
    list_id: int
    created_at: datetime
    completed: bool
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class ListBase(BaseModel):
    title: str
    description: str | None = None


class ListCreate(ListBase):
    pass


class ListUpdate(BaseModel):  # 继承 BaseModel 避免继承 title
    title: str | None = None
    description: str | None = None


class ListResponse(ListBase):
    id: int
    user_id: UUID
    todos: list[TodoResponse] | None = None

    model_config = ConfigDict(from_attributes=True)