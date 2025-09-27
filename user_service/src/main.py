from fastapi import FastAPI, Response, Depends

from src.core.lifespan import lifespan
from src.core.config import settings
from src.core.middleware import add_cors_middleware
from src.users.models import User
from src.users.routes import include_user_routers
from src.users.user_manager import current_active_user


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

# 中间件
add_cors_middleware(app)


# 路由
include_user_routers(app)


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

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
