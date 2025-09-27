# src/core/lifespan.py
from typing import TypedDict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)

from src.core.config import get_settings
from src.core.database import (
    setup_database_connection,
    close_database_connection,
    create_db_and_tables,
)
from src.core.redis_db import setup_redis, close_redis


class AppState(TypedDict):
    """
    定义应用生命周期中共享状态的结构。
    这为类型检查器和编辑器提供了明确的类型信息。
    """

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[AppState]:
    # -------- 启动 --------
    get_settings()
    logger.info("🚀 应用启动，配置已就绪。")
    engine, session_factory = await setup_database_connection()
    logger.info("数据库已就绪。")
    await create_db_and_tables(engine)
    redis = await setup_redis()
    logger.info("Redis 已就绪。")

    yield {"engine": engine, "session_factory": session_factory, "redis": redis}

    # -------- 关闭 --------
    await close_database_connection(engine)
    await close_redis(redis)
    logger.info("应用关闭，资源已释放。")
