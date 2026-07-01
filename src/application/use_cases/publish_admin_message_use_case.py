import structlog

from src.application.dto.admin_message import AdminMessage
from src.application.interfaces.broker.publisher import BrokerPublisher


class PublishAdminMessageUseCase:
    def __init__(
            self,
            logger: structlog.BoundLogger,
            broker_publisher: BrokerPublisher,
    ):
        self._logger = logger
        self._broker_publish = broker_publisher

    async def __call__(self, payload: AdminMessage):
        await self._broker_publish.publish_admin_message(payload)
