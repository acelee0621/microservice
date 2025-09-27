from fastapi import Depends, FastAPI, Response

from src.core.config import settings
from src.core.lifespan import lifespan
from src.core.middleware import add_cors_middleware
from src.core.exceptions import register_exception_handlers
from src.core.auth import get_current_user
from src.todos.schemas import UserRead
from src.todos import routes_todos, routes_list


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

# 中间件
add_cors_middleware(app)

# 全局异常处理
register_exception_handlers(app)

app.include_router(routes_list.router)
app.include_router(routes_todos.router)


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
