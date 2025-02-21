from datetime import datetime, timezone
import enum
from typing import Optional
from uuid import UUID
from sqlalchemy import (
    Boolean,
    Integer,
    String,
    Text,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


# 基础类
class Base(DeclarativeBase):
    pass


class Priority(enum.Enum):
    low = 1
    medium = 2
    high = 3


class TodoList(Base):
    __tablename__ = "lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64), default="My List", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    todos: Mapped[list["Todos"]] = relationship(
        "Todos", back_populates="list", cascade="all, delete-orphan", lazy="selectin"
    )
    # 唯一约束（确保同一用户的列表标题不重复）
    __table_args__ = (
        UniqueConstraint("title", "user_id", name="unique_user_list_title"),
    )


class Todos(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[Enum] = mapped_column(
        Enum(Priority),
        default=Priority.low,
        nullable=False,
        comment="Priority, 1-low, 2-medium, 3-high",
    )
    created_at: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    completed: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, nullable=False
    )
    list_id: Mapped[int] = mapped_column(
        ForeignKey("lists.id"), index=True, nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    list: Mapped["TodoList"] = relationship("TodoList", back_populates="todos")
