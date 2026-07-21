from abc import abstractmethod
from typing import Protocol

from src.application.interfaces.postgres.repositories.message_repository import PostgresMessageRepository
from src.application.interfaces.postgres.repositories.ticket_repository import PostgresTicketRepository


class UnitOfWork(Protocol):

    @property
    def message(self) -> PostgresMessageRepository:
        ...

    @property
    def ticket(self) -> PostgresTicketRepository:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...
