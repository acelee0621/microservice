import httpx
from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import create_db_and_tables
from app.core.redis_db import redis_connect
from app.core.auth import get_current_user
from app.schemas.schemas import UserRead
from app.routers import lists_routes, todos_route, notification


# Set up logging configuration
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("启动: 创建 Redis 连接池及HTTPx 客户端...")
    app.state.cache_redis = await redis_connect()
    app.state.http_client = httpx.AsyncClient()    
    # await create_db_and_tables()
    yield
    print("关闭: 释放 Redis 连接池及关闭及HTTPx 客户端...")
    await app.state.cache_redis.aclose()
    await app.state.http_client.aclose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(lists_routes.router)
app.include_router(todos_route.router)
app.include_router(notification.router)


@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}


@app.get("/protected-route")
async def protected_route(current_user: UserRead = Depends(get_current_user)):
    """Protected route"""
    return {"message": "This is a protected route", "user": current_user}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
