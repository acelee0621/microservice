# src/core/redis_db.py
from typing import cast

from fastapi import Request
from redis.asyncio import Redis

from src.core.config import settings


async def setup_redis() -> Redis:
    """启动时创建异步 Redis 连接池"""
    redis = Redis.from_url(
        f"redis://{settings.redis_host}",
        db=0,
        decode_responses=True,
    )
    await redis.ping()  # 确认连通性
    return redis


async def close_redis(redis: Redis) -> None:
    """关闭时优雅释放连接池"""
    await redis.aclose()


async def get_redis(request: Request) -> Redis:
    """从 lifespan.state 里拿初始化好的 redis 实例"""
    return cast(Redis, request.state.redis)
