# src/core/database.py
from typing import AsyncGenerator, cast

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from loguru import logger
from fastapi import Depends, Request
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase

from src.core.config import settings
from src.core.models import Base
from src.users.models import User, AccessToken


# --- 1. 数据库初始化和关闭函数 ---
async def setup_database_connection() -> tuple[
    AsyncEngine, async_sessionmaker[AsyncSession]
]:
    """
    初始化数据库引擎和会话工厂。
    lifespan 会在 FastAPI 启动时调用本函数。
    """

    # 创建异步引擎
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.echo,
    )

    # 创建会话工厂
    session_factory = async_sessionmaker(
        class_=AsyncSession, expire_on_commit=False, bind=engine
    )

    logger.info("数据库引擎和会话工厂已创建")
    return engine, session_factory


async def close_database_connection(engine: AsyncEngine) -> None:
    """
    关闭数据库引擎连接池。
    lifespan 会在 FastAPI 关闭时调用本函数。
    """
    await engine.dispose()
    logger.info("数据库引擎连接池已关闭。")


# --- 2. 依赖注入函数 ---
async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    为每个请求或任务提供数据库会话。
    它依赖于 lifespan 中初始化的 session_factory。
    """

    session_factory = cast(
        async_sessionmaker[AsyncSession], request.state.session_factory
    )
    async with session_factory() as session:
        yield session


# --- 4. 数据库表创建工具 ---
async def create_db_and_tables(engine: AsyncEngine) -> None:
    """
    使用给定的引擎创建所有数据库表。
    推荐在应用启动时调用（仅开发环境需要，生产环境一般使用 Alembic 迁移）。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建成功。")


# --- 5. FastAPI Users 专用 ---
async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
    session: AsyncSession = Depends(get_db),
):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
