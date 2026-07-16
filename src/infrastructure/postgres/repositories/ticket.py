from src.application.interfaces.postgres.repository.ticket_repository import PostgresTicketRepository
from src.domain.entities.ticket import Ticket
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.values import TicketId, ClientId

from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.infrastructure.postgres.tables import tickets_table


class ImplPostgresTicketRepository(PostgresTicketRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entity: Ticket) -> None:
        stmt = pg_insert(tickets_table).values(
            id=entity.id.value,
            status=entity.status.value,
            client_id=entity.client_id.value,
            created_at=entity.created_at,
            last_activity_at=entity.last_activity_at,
            closed_at=entity.closed_at,
            close_reason=entity.close_reason.value if entity.close_reason else None,
            admin_id=entity.admin_id.value if entity.admin_id else None,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "status": stmt.excluded.status,
                "last_activity_at": stmt.excluded.last_activity_at,
                "closed_at": stmt.excluded.closed_at,
                "close_reason": stmt.excluded.close_reason,
                "admin_id": stmt.excluded.admin_id,
            },
        )
        await self._session.execute(stmt)

    async def get(self, uid: TicketId):
        raise NotImplementedError

    async def find_active_by_client(self, client_id: ClientId) -> Ticket | None:
        raise NotImplementedError
