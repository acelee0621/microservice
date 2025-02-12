from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy import Boolean, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


# 基础类
class Base(DeclarativeBase):
    pass


class TodoList(Base):
    __tablename__ = "lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(64), default="My List", index=True, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # 改为普通字段（不再关联外键）
    user_id: Mapped[UUID] = mapped_column(nullable=False)

    # 一对多关系保留（与 Todo 的关系）
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="list", cascade="all, delete-orphan", lazy=False
    )
    # 唯一约束保留（确保同一用户的列表标题不重复）
    __table_args__ = (
        UniqueConstraint("title", "user_id", name="unique_user_list_title"),
    )


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    completed: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, nullable=False
    )
    # 外键保留（关联业务数据库的 List 表）
    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"), nullable=False)
    # 改为普通字段（不再关联外键）
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    # 保留与 List 的关系
    list: Mapped["TodoList"] = relationship("TodoList", back_populates="todos")
