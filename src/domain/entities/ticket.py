from src.domain.values import TicketId, ClientId, AdminId, TicketStatus
from datetime import datetime


class Ticket:
    def __init__(
            self,
            *,
            uid: TicketId,
            client_id: ClientId,
            status: TicketStatus,
            assigned_admin_id: AdminId | None = None,
            created_at: datetime,
            last_activity_at: datetime,
            closed_at: datetime,
    ):
        self._id = uid
        self._client_id = client_id
        self._assigned_admin_id = assigned_admin_id
        self._status = status

        self._created_at = created_at
        self._last_activity_at = last_activity_at
        self._closed_at = closed_at

    @property
    def id(self) -> TicketId:
        return self._id

    @property
    def status(self) -> TicketStatus:
        return self._status

    @property
    def client_id(self) -> ClientId:
        return self._client_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def last_activity_at(self) -> datetime:
        return self._last_activity_at

    @property
    def closed_at(self) -> datetime | None:
        return self._closed_at

    @property
    def admin_id(self) -> AdminId | None:
        return self._assigned_admin_id

    @classmethod
    def open(cls, *, client_id: ClientId, now: datetime) -> "Ticket":
        return cls(
            uid=TicketId.new(),
            client_id=client_id,
            status=TicketStatus.initial(),
            created_at=now,
            last_activity_at=now,
            closed_at=None
        )
