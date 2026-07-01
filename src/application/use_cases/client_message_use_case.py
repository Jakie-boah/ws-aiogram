import structlog

from src.application.dto.client_message import ClientMessageDTO
from src.application.interfaces.redis.storage import RedisStorage
from src.application.interfaces.tg.api import TgAPI
from src.domain.mapper import map_client_message_from_dto


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

    async def __call__(self, payload: ClientMessageDTO):
        client_message = map_client_message_from_dto(payload)

        message_id = await self.tg_api.send_message(client_message.text)
        await self.storage.set(message_id, client_message.user_id)
