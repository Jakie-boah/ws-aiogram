from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.postgres.repositories.message_repository import PostgresMessageRepository
from src.application.interfaces.postgres.repositories.ticket_repository import PostgresTicketRepository
from src.application.interfaces.postgres.uow import UnitOfWork
from src.infrastructure.postgres.repositories.message import ImplPostgresMessageRepository
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository
from sqlalchemy.exc import SQLAlchemyError


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

    async def commit(self) -> None:
        try:
            await self._session.commit()

        except SQLAlchemyError:
            await self.rollback()
            raise

    async def rollback(self) -> None:
        await self._session.rollback()
