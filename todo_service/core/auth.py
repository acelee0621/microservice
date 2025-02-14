import json
from httpx import AsyncClient, HTTPStatusError, RequestError
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from todo_service.core.dependencies import get_http_client
from todo_service.core.redis_db import get_cache_redis
from todo_service.todos.schemas import UserRead

# 用户管理微服务的 URL
USER_SERVICE_URL = "http://127.0.0.1:8000"

# 定义 OAuth2 令牌 URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{USER_SERVICE_URL}/auth/redis/login")


async def get_current_user(
    token: str = Security(oauth2_scheme),
    redis: Redis = Depends(get_cache_redis),
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
            f"{USER_SERVICE_URL}/users/me", headers=headers
        )
        response.raise_for_status()
    except HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Invalid authentication credentials",
        )
    except RequestError:
        raise HTTPException(status_code=503, detail="User service unavailable")

    user_data = response.json()

    # 3. 将用户信息缓存到 Redis，并设置过期时间
    await redis.setex(f"user:{token}", 3600, json.dumps(user_data))

    return UserRead.model_validate(user_data)
