import json
import asyncio
import aio_pika
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["Notifications"])

# 存储活跃的 WebSocket 连接
active_connections = []


async def rabbit_consumer(websocket: WebSocket):
    # 连接 RabbitMQ
    connection = await aio_pika.connect_robust("amqp://admin:admin@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("todo_notifications", durable=True)

    # 消费消息
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():  # 自动确认消息
                message_body = message.body.decode()
                message_data = json.loads(message_body)
                # 处理过的消息，转换为 JSON 字符串
                message_str = json.dumps(
                    message_data, ensure_ascii=False
                )  
                await websocket.send_text(message_str)  # 推送给客户端


@router.websocket("/notification/todo")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"New WebSocket connection, total: {len(active_connections)}")

    # 启动 RabbitMQ 消费者
    consumer_task = asyncio.create_task(rabbit_consumer(websocket))

    try:
        while True:
            await websocket.receive_text()  # 保持连接活跃
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        consumer_task.cancel()  # 断开时取消消费者任务
        print(f"WebSocket disconnected, total: {len(active_connections)}")
    finally:
        await websocket.close()
