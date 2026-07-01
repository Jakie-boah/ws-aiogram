import structlog
from faststream.rabbit import RabbitBroker

from src.application.interfaces.broker.publisher import BrokerPublisher
from src.domain.entities.admin_message import AdminMessage
from src.domain.entities.client_message import ClientMessage


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

    async def publish_client_message(self, entity: ClientMessage):
        await self.broker.publish(
            message=entity.as_dict(),
            exchange="chat", routing_key="client_message",
        )

    async def publish_admin_message(self, entity: AdminMessage):
        await self.broker.publish(
            message=entity.as_dict(),
            exchange="chat", routing_key="admin_message"
        )
