import structlog

from src.application.dto.admin_message import AdminMessageDTOV0
from src.application.interfaces.broker.publisher import BrokerPublisher
from src.domain.entities.admin_message import AdminMessage
from src.domain.mapper import map_admin_message_from_dto


class PublishAdminMessageUseCase:
    def __init__(
            self,
            logger: structlog.BoundLogger,
            broker_publisher: BrokerPublisher,
    ):
        self._logger = logger
        self._broker_publish = broker_publisher

    async def __call__(self, payload: AdminMessageDTOV0):
        admin_message: AdminMessage = map_admin_message_from_dto(payload)
        await self._broker_publish.publish_admin_message(admin_message)
