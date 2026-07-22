from abc import abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from src.application.interfaces.postgres.repositories.message_repository import PostgresMessageRepository
from src.application.interfaces.postgres.repositories.ticket_repository import PostgresTicketRepository


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
        """Вложенная транзакция. При исключении внутри блока откатывается
        только она — внешняя транзакция остаётся рабочей."""
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...
