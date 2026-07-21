from src.application.interfaces.postgres.repositories.base import Repository

from typing import Protocol
from src.domain.values import MessageId, TicketId
from src.domain.entities.message import Message
from abc import abstractmethod


class PostgresMessageRepository(Repository[Message, MessageId], Protocol):
    @abstractmethod
    async def find_undelivered_by_ticket_id(self, *, ticket_id: TicketId) -> list[Message]:
        ...
