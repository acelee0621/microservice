from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID

from app.models.models import Priority


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool


class TodoBase(BaseModel):
    content: str
    priority: str


class TodoCreate(TodoBase):
    pass

    @field_validator("priority")
    def validate_priority(cls, value):
        # 将字符串转换为枚举值
        try:
            return Priority[value]  # 例如 "low" -> Priority.low
        except KeyError:
            raise ValueError(
                f"Invalid priority: {value}. Must be one of {[e.name for e in Priority]}"
            )


class TodoUpdate(BaseModel):  # 继承 BaseModel 避免继承 title
    content: str | None = None
    priority: str | None = None
    completed: bool | None = None  # 避免默认 False
    
    @field_validator("priority")
    def validate_priority(cls, value):
        # 将字符串转换为枚举值
        try:
            return Priority[value]  # 例如 "low" -> Priority.low
        except KeyError:
            raise ValueError(
                f"Invalid priority: {value}. Must be one of {[e.name for e in Priority]}"
            )


class TodoResponse(TodoBase):
    id: int
    list_id: int
    created_at: datetime
    completed: bool
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)

    # 使用 field_validator 转换 priority 字段的值
    @field_validator("priority", mode="before")
    def convert_priority(cls, value):
        if isinstance(value, Priority):
            return value.name  # 将枚举值转换为字符串名称
        return value

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
