from src.application.interfaces.postgres.repository.base import Repository

from typing import Protocol
from src.domain.values import TicketId, ClientId
from src.domain.entities.ticket import Ticket
from abc import abstractmethod


class PostgresTicketRepository(Repository[Ticket, TicketId], Protocol):
    @abstractmethod
    async def find_active_by_client(self, client_id: ClientId) -> Ticket | None: ...
