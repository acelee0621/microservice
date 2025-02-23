import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.rabbitmq import RabbitMQClient
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Notifications"])


active_connections = []

async def process_message_for_websocket(message: dict, websocket: WebSocket):
    """处理 RabbitMQ 消息，并通过 WebSocket 发送给客户端"""
    message_str = json.dumps(message, ensure_ascii=False)
    await websocket.send_text(message_str)
    logger.info(f"Sent message to WebSocket: {message}")

@router.websocket("/notification/todo")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"新的WebSocket连接,当前总数: {len(active_connections)}")

    rabbitmq_client = RabbitMQClient()
    consumer_task = asyncio.create_task(
        rabbitmq_client.consume_messages(
            queue="todo_notifications",
            callback=lambda msg: process_message_for_websocket(msg, websocket)
        )
    )

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        consumer_task.cancel()
        await rabbitmq_client.close()
        logger.info(f"WebSocket断开,当前总数: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
    finally:
        await websocket.close()