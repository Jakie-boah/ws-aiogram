import structlog

from src.application.dto.admin_message import AdminMessage, AdminReply
from src.application.interfaces.redis.storage import RedisStorage
from src.application.services.broker.publish import PublisherService


class AdminMessageUseCase:
    def __init__(
            self,
            logger: structlog.BoundLogger,
            storage: RedisStorage,
            publisher: PublisherService,
    ):
        self._logger = logger
        self.storage = storage
        self.publisher = publisher

    async def __call__(self, payload: AdminMessage):
        user_id = await self.storage.get(payload.client_message_id)

        payload = AdminReply(
            text=payload.text.value,
            user_id=user_id.value
        )
        await self.publisher.publish_admin_message(payload)
