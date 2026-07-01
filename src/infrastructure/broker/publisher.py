import structlog
from faststream.rabbit import RabbitBroker

from src.application.dto.client_message import ClientMessage
from src.application.interfaces.broker.publisher import BrokerPublisher


class ImplBrokerPublisher(BrokerPublisher):
    def __init__(
            self,
            logger: structlog.BoundLogger,
            broker: RabbitBroker
    ):
        self._logger = logger
        self._broker = broker

    @property
    def broker(self) -> RabbitBroker:
        return self._broker

    async def publish_client_message(self, payload: ClientMessage):
        await self.broker.publish(
            message=payload.as_dict(),
            exchange="chat", routing_key="client_message",
        )

    async def publish_admin_message(self):
        pass
