# src/core/exceptions.py
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

class NotFoundException(HTTPException):
    """Base exception for resource not found errors."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsException(HTTPException):
    """Base exception for resource already exists errors."""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnauthorizedException(HTTPException):
    """Base exception for unauthorized access errors."""

    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    """Base exception for forbidden access errors."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        
        
# ------------------ 全局兜底 ------------------
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
    
    
# 👇 新增一个专门用于注册的函数
def register_exception_handlers(app: FastAPI) -> None:
    """向 FastAPI app 实例注册全局异常处理器。"""
    app.add_exception_handler(Exception, global_exception_handler)
    
    # 如果未来有其他需要注册的，都加在这里
    # app.add_exception_handler(SomeOtherLibraryError, handle_other_error)