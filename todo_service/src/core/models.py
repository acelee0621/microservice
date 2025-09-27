# src/core/database/base.py
from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

# --- 基类 ---
class Base(DeclarativeBase):
    pass


# --- 时间日期混入 ---
class DateTimeMixin:    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),  # 插入时用应用层时间
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),  # 更新时用应用层时间
        nullable=False,
    )