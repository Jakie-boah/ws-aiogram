from abc import abstractmethod
from typing import Protocol, runtime_checkable

from src.application.interfaces.postgres.repositories.base import Repository
from src.domain.entities.message import Message
from src.domain.values import MessageId, TicketId


@runtime_checkable
class PostgresMessageRepository(Repository[Message, MessageId], Protocol):
    @abstractmethod
    async def find_undelivered_by_ticket_id(self, *, ticket_id: TicketId) -> list[Message]:
        ...
