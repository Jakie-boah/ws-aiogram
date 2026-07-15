from src.domain.values import TicketId, ClientId, AdminId, TicketStatus, TicketCloseReason
from datetime import datetime
from src.domain.errors.entities.ticket import AdminAlreadyAssignedError, AdminIsNotAssignedError, TicketIsClosedError


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
            closed_at: datetime | None = None,
            close_reason: TicketCloseReason | None = None
    ):
        self._id = uid
        self._client_id = client_id
        self._assigned_admin_id = assigned_admin_id
        self._status = status

        self._created_at = created_at
        self._last_activity_at = last_activity_at
        self._closed_at = closed_at
        self._close_reason = close_reason

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
    def close_reason(self) -> TicketCloseReason | None:
        return self._close_reason

    @property
    def admin_id(self) -> AdminId | None:
        return self._assigned_admin_id

    @classmethod
    def open(
            cls,
            *,
            client_id: ClientId,
            now: datetime
    ) -> "Ticket":
        return cls(
            uid=TicketId.new(),
            client_id=client_id,
            status=TicketStatus.initial(),
            created_at=now,
            last_activity_at=now,
        )

    def register_client_message(self, now: datetime):
        if self._status.is_closed():
            raise TicketIsClosedError(field="status", message="Ticket is closed. Cannot register client message")

        self._status = self._status.on_client_message()
        self._set_last_activity(now)

    def register_admin_message(self, now: datetime):
        if self._status.is_closed():
            raise TicketIsClosedError(
                field="status",
                message="Ticket was closed."
            )

        if self._assigned_admin_id is None:
            raise AdminIsNotAssignedError(
                field="assigned_admin_id",
                message="Admin is not assigned. Cannot register message"
            )

        self._status = self._status.on_admin_message()
        self._set_last_activity(now)

    def _set_last_activity(self, now: datetime):
        self._last_activity_at = now

    def assign_admin(self, admin_id: AdminId):
        if self._status.is_closed():
            raise TicketIsClosedError(
                field="status",
                message="Ticket is closed. Cannot assign admin"
            )

        if self._assigned_admin_id is not None:
            raise AdminAlreadyAssignedError(field="assigned_admin_id", message="Admin already assigned")

        self._assigned_admin_id = admin_id

    def close(self, *, reason: TicketCloseReason, now: datetime):
        if self._status.is_closed():
            raise TicketIsClosedError(field="status", message="Ticket is already closed")

        self._status = self._status.on_close()
        self._close_reason = reason

        self._closed_at = now
        self._set_last_activity(now)
