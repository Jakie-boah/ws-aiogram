from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.postgres.repositories.message_repository import PostgresMessageRepository
from src.application.interfaces.postgres.repositories.ticket_repository import PostgresTicketRepository
from src.application.interfaces.postgres.uow import UnitOfWork
from src.infrastructure.postgres.repositories.message import ImplPostgresMessageRepository
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository
from contextlib import asynccontextmanager
from typing import AsyncIterator


class ImplUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._message = ImplPostgresMessageRepository(self._session)
        self._ticket = ImplPostgresTicketRepository(self._session)

    @property
    def message(self) -> PostgresMessageRepository:
        return self._message

    @property
    def ticket(self) -> PostgresTicketRepository:
        return self._ticket

    @asynccontextmanager
    async def savepoint(self) -> AsyncIterator[None]:
        async with self._session.begin_nested():
            yield

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
