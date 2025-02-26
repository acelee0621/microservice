from fastapi import FastAPI, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import User
from app.schemas import UserCreate, UserRead, UserUpdate
from app.user_manage import auth_backend, current_active_user, fastapi_users
from app.core.redis_db import redis_connect
from app.utils.migrations import run_migrations


# Optional: Run migrations on startup
run_migrations()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("启动: 创建 Redis 连接池...")
    app.state.auth_redis = await redis_connect()    
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
@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
