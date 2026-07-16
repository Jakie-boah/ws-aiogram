from src.application.interfaces.postgres.repository.ticket_repository import PostgresTicketRepository
from src.domain.entities.ticket import Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.values import TicketId, ClientId


class ImplPostgresTicketRepository(PostgresTicketRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entity: Ticket):
        raise NotImplementedError

    async def get(self, uid: TicketId):
        raise NotImplementedError

    async def find_active_by_client(self, client_id: ClientId) -> Ticket | None:
        raise NotImplementedError
