from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# 配置 CORS（按需调整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义后端服务配置
SERVICES = {
    "user_service": {
        "base_url": "http://127.0.0.1:8001",
        "paths": ["/auth", "/users", "/server-status"]
    },
    "todo_service": {
        "base_url": "http://127.0.0.1:8002",
        "paths": ["/lists", "/todos", "/protected-route"]
    }
}

async def forward_request(request: Request, service_url: str):
    client = httpx.AsyncClient(base_url=service_url)
    url_path = request.url.path
    headers = dict(request.headers)
    
    # 移除可能冲突的 headers
    headers.pop("host", None)
    headers.pop("content-length", None)

    # 确保 Content-Type 是 application/json
    if "content-type" not in headers:
        headers["content-type"] = "application/json"

    try:
        # 获取请求体
        body = await request.body()
        
        # 转发请求
        response = await client.request(
            method=request.method,
            url=url_path,
            headers=headers,
            params=request.query_params,
            content=body
        )
        
        # 提取响应数据
        return {
            "status_code": response.status_code,
            "content": response.content,
            "headers": dict(response.headers),
        }
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    finally:
        await client.aclose()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway_proxy(request: Request):
    path = request.url.path
    
    # 路由判断逻辑
    if any(path.startswith(p) for p in SERVICES["user_service"]["paths"]):
        service = SERVICES["user_service"]
    elif any(path.startswith(p) for p in SERVICES["todo_service"]["paths"]):
        service = SERVICES["todo_service"]
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    # 转发请求
    response_data = await forward_request(request, service["base_url"])
    
    # 返回响应
    return Response(
        content=response_data["content"],
        status_code=response_data["status_code"],
        headers=response_data["headers"],
    )