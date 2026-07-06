import structlog

from src.application.dto.client_message import ClientMessageDTO
from src.application.interfaces.broker.publisher import BrokerPublisher
from src.domain.entities.client_message import ClientMessage
from src.domain.mapper import map_client_message_from_dto


class PublishClientMessageUseCase:
    def __init__(
            self,
            logger: structlog.BoundLogger,
            broker_publisher: BrokerPublisher,
    ):
        self._logger = logger
        self._broker_publisher = broker_publisher

    async def __call__(self, data: ClientMessageDTO):
        client_message: ClientMessage = map_client_message_from_dto(data)

        await self._broker_publisher.publish_client_message(client_message)
