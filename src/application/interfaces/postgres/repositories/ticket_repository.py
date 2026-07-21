from abc import abstractmethod
from typing import Protocol

from src.application.interfaces.postgres.repositories.base import Repository
from src.domain.entities.ticket import Ticket
from src.domain.values import ClientId, TicketId


class PostgresTicketRepository(Repository[Ticket, TicketId], Protocol):
    @abstractmethod
    async def find_active_by_client(self, client_id: ClientId) -> Ticket | None: ...
