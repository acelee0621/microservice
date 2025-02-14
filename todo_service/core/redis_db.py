from fastapi import Request
from redis.asyncio import Redis, ConnectionPool

from todo_service.core.config import config


cache_pool = ConnectionPool.from_url(
    config.REDIS_URL, db=0, max_connections=10, decode_responses=True
)


async def redis_connect():
    try:
        redis_client = Redis(connection_pool=cache_pool)
        is_connected = await redis_client.ping()
        if is_connected:
            print("redis连接成功")
        return redis_client
    except ConnectionError:
        print("redis连接失败")
    except TimeoutError:
        print("redis连接超时")
    except Exception as e:
        print("redis连接异常", e)
        
        
async def get_cache_redis(request:Request) -> Redis:
    return request.app.state.cache_redis
