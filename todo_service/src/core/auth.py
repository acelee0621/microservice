import json
from loguru import logger
from httpx import AsyncClient, HTTPStatusError, RequestError
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from src.core.dependencies import get_http_client
from src.core.config import settings
from src.core.redis_db import get_redis
from src.todos.schemas import UserRead

user_service_url = settings.user_service_url

# 定义 OAuth2 令牌 URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{user_service_url}/auth/jwt/login")


async def get_current_user(
    token: str = Security(oauth2_scheme),
    redis: Redis = Depends(get_redis),
    http_client: AsyncClient = Depends(get_http_client),
) -> UserRead:
    """通过 Redis 缓存和用户管理微服务验证令牌，获取当前用户信息"""

    # 1. 先查询 Redis 缓存是否已有用户信息
    cached_user = await redis.get(f"user:{token}")
    if cached_user:
        return UserRead.model_validate(json.loads(cached_user))

    # 2. 如果 Redis 缓存没有用户信息，向用户管理微服务验证令牌
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = await http_client.get(
            f"{user_service_url}/users/me", headers=headers
        )
        response.raise_for_status()
    except HTTPStatusError as exc:
        await redis.delete(f"user:{token}")  # 清除缓存
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Invalid authentication credentials",
        )
    except RequestError:
        logger.error("User service is unavailable")
        raise HTTPException(status_code=503, detail="User service unavailable")

    user_data = response.json()

    # 3. 将用户信息缓存到 Redis，并设置过期时间
    await redis.setex(f"user:{token}", 3600, json.dumps(user_data))

    return UserRead.model_validate(user_data)
