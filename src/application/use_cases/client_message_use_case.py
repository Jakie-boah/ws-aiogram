import structlog

from src.application.dto.client_message import ClientMessage
from src.application.interfaces.redis.storage import RedisStorage
from src.application.interfaces.tg.api import TgAPI
from src.domain.values import Text, UserId


class ClientMessageUseCase:
    def __init__(
            self,
            logger: structlog.BoundLogger,
            tg_api: TgAPI,
            redis_storage: RedisStorage,
    ):
        self.logger = logger
        self.tg_api = tg_api
        self.storage = redis_storage

    async def __call__(self, payload: ClientMessage):
        user_id = UserId(int(payload.user_id))
        text = Text(payload.text)

        message_id = await self.tg_api.send_message(text)
        await self.storage.set(message_id, user_id)
