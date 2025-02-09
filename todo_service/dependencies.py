from fastapi import Request, Depends
from typing import Annotated
import httpx
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from todo_service.database import get_db




# 数据库依赖
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]


# HTTP 客户端依赖
async def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]


# Redis 依赖
async def get_cache_redis(request:Request) -> Redis:
    return request.app.state.cache_redis

CacheRedisDep = Annotated[Redis, Depends(get_cache_redis)]




