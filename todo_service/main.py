import sys
import httpx
from fastapi import FastAPI, Response, status, __version__ as fastapi_version
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from todo_service.config import config
from todo_service.routers import lists, todos
from todo_service.database import create_db_and_tables
from todo_service.redis_db import redis_connect
from todo_service.auth import CurrentUserDep


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("启动: 创建 Redis 连接池及HTTPx 客户端...")
    app.state.cache_redis = await redis_connect()
    app.state.http_client = httpx.AsyncClient()
    await create_db_and_tables()
    yield
    print("关闭: 释放 Redis 连接池及关闭及HTTPx 客户端...")
    await app.state.cache_redis.aclose()
    await app.state.http_client.aclose()


app = FastAPI(title=config.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(lists.router)
app.include_router(todos.router)


@app.get("/server-status", include_in_schema=False)
async def health_check(response: Response, token: str | None = None):
    if token == "Ace":
        response.status_code = 200
        data = {
            "status": "ok 👍 ",
            "FastAPI Version": fastapi_version,
            "Python Version": sys.version_info,
        }
        return data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND  # 404
        return {"detail": "Not Found ❌"}


@app.get("/protected-route")
async def protected_route(current_user: CurrentUserDep):
    """受保护的业务路由"""
    return {"message": "This is a protected route", "user": current_user}
