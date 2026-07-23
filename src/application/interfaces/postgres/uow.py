from abc import abstractmethod
from typing import Protocol

from src.application.interfaces.postgres.repositories.message_repository import PostgresMessageRepository
from src.application.interfaces.postgres.repositories.ticket_repository import PostgresTicketRepository
from contextlib import AbstractAsyncContextManager


class UnitOfWork(Protocol):

    @property
    @abstractmethod
    def message(self) -> PostgresMessageRepository:
        ...

    @property
    @abstractmethod
    def ticket(self) -> PostgresTicketRepository:
        ...

    @abstractmethod
    def savepoint(self) -> AbstractAsyncContextManager[None]:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...
