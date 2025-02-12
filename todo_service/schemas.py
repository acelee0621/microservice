from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: str | None = None


class ListBase(BaseModel):
    title: str
    description: str | None = None

    class Config:
        from_attributes = True


class ListOut(ListBase):
    id: int
    user_id: UUID
    todos: list["TodoOut"] | None = None

    class Config:
        from_attributes = True


class ListCreate(ListBase):
    user_id: UUID
    

class ListCreateOut(ListBase):
    id: int
    user_id: UUID
    
    class Config:
        from_attributes = True


class ListUpdate(ListBase):
    title: str | None = None


class ListUpdateOut(ListBase):
    id: int

    class Config:
        from_attributes = True


class TodoBase(BaseModel):
    title: str
    description: str | None = None


class TodoOut(TodoBase):
    id: int
    list_id: int
    created_at: datetime
    completed: bool

    class Config:
        from_attributes = True


class TodoCreate(TodoBase):
    list_id: int


class TodoUpdate(TodoBase):
    title: str | None = None
    completed: bool | None = False
