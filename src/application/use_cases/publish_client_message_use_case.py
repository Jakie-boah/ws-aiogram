import structlog

from src.application.interfaces.broker.publisher import BrokerPublisher
from src.domain.entities.client_message import ClientMessage


class PublishClientMessageUseCase:
    def __init__(
            self,
            logger: structlog.BoundLogger,
            broker_publisher: BrokerPublisher,
    ):
        self._logger = logger
        self._broker_publisher = broker_publisher

    async def __call__(self, data: ClientMessage):
        await self._broker_publisher.publish_client_message(data)
