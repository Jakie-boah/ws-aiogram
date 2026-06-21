from dataclasses import asdict

import structlog
from faststream.rabbit import RabbitBroker

from src.application.dto.admin_message import AdminReply
from src.application.dto.client_message import ClientMessage


class PublisherService:
    def __init__(self, logger: structlog.BoundLogger, rabbit: RabbitBroker):
        self.logger = logger
        self.rabbit = rabbit

    async def publish_client_message(self, payload: ClientMessage):
        await self.rabbit.publish(
            message=asdict(payload),
            exchange="chat", routing_key="client_message",
        )

    async def publish_admin_message(self, payload: AdminReply):
        await self.rabbit.publish(
            message=asdict(payload),
            exchange="chat", routing_key="admin_message",
        )
