import sys

from fastapi import FastAPI, Response, status, Depends, __version__ as fastapi_version
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from user_service.database import User, create_db_and_tables
from user_service.schemas import UserCreate, UserRead, UserUpdate
from user_service.user_manage import auth_backend, current_active_user, fastapi_users
from user_service.redis_db import redis_connect


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("启动: 创建 Redis 连接池...")
    app.state.auth_redis = await redis_connect()
    await create_db_and_tables()
    yield
    print("关闭: 释放 Redis 连接池...")
    await app.state.auth_redis.aclose()


app = FastAPI(title="User Service", version="0.1.0", lifespan=lifespan)

# 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 路由
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/redis", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


# 状态检查
@app.get("/server-status")
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


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
