import json
from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection


async def get_rabbitmq_connection() -> AbstractRobustConnection:
    return await connect_robust("amqp://admin:admin@localhost/")


class RabbitMQClient:
    def __init__(
        self, host="amqp://admin:admin@localhost/", queue="todo_notifications"
    ):
        self.host = host
        self.queue = queue

    async def send_message(self, message: dict):
        try:
            # 连接到 RabbitMQ
            connection = await connect_robust(self.host)
            async with connection:
                # 创建一个通道
                channel = await connection.channel()
                # 声明一个持久化的队列
                await channel.declare_queue(self.queue, durable=True)
                # 创建消息对象
                message_body = json.dumps(message).encode()
                message = Message(
                    body=message_body,
                    delivery_mode=DeliveryMode.PERSISTENT,  # 使消息持久化
                )
                # 发布消息
                await channel.default_exchange.publish(message, routing_key=self.queue)
                print(f" [x] Sent message to {self.queue}")
        except Exception as e:
            print(f"Failed to send message to RabbitMQ: {e}")
