from typing import Protocol

from faststream.rabbit import RabbitBroker

from src.application.dto.client_message import ClientMessage


class BrokerPublisher(Protocol):

    @property
    def broker(self) -> RabbitBroker:
        ...

    async def publish_client_message(self, payload: ClientMessage) -> None:
        ...

    async def publish_admin_message(self) -> None:
        ...
