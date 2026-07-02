import structlog
from src.application.interfaces.redis.storage import RedisStorage
from src.application.dto.admin_message import AdminMessageDTO
from src.domain.mapper import map_admin_message_from_dto
from src.domain.entities.admin_message import AdminMessage
from src.domain.values import UserId


class AdminMessageUseCase:
    def __init__(
            self,
            logger: structlog.BoundLogger,
            redis_storage: RedisStorage,
    ):
        self._logger = logger
        self._redis_storage = redis_storage

    async def __call__(self, payload: AdminMessageDTO):
        admin_message: AdminMessage = map_admin_message_from_dto(payload)
        user_id: UserId = await self._redis_storage.get(admin_message.message_id)
        raise NotImplementedError
        # await self._aio_requests.send()
