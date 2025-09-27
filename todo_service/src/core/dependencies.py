from fastapi import Request
import httpx

# HTTP 客户端依赖
async def get_http_client(request: Request) -> httpx.AsyncClient:
    return httpx.AsyncClient()










