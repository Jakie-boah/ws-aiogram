from typing import Protocol

from faststream.rabbit import RabbitBroker

from src.domain.entities.admin_message import AdminMessage
from src.domain.entities.client_message import ClientMessage


class BrokerPublisher(Protocol):

    @property
    def broker(self) -> RabbitBroker:
        ...

    async def publish_client_message(self, entity: ClientMessage) -> None:
        ...

    async def publish_admin_message(self, entity: AdminMessage) -> None:
        ...
