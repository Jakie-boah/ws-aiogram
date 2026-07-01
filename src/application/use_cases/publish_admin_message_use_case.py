import structlog

from src.application.interfaces.broker.publisher import BrokerPublisher
from src.domain.entities.admin_message import AdminMessage


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
