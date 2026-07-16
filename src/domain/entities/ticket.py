from datetime import datetime

from src.domain.errors.entities import ticket as ticket_errors
from src.domain.values import AdminId, ClientId, TicketCloseReason, TicketId, TicketStatus


_DT_FMT = "%Y-%m-%d %H:%M:%S.%f%z"


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
        self._validate()

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
            uid=TicketId.generate(),
            client_id=client_id,
            status=TicketStatus.initial(),
            created_at=now,
            last_activity_at=now,
        )

    def register_client_message(self, now: datetime):
        if self._status.is_closed():
            raise ticket_errors.TicketIsClosedError(
                field="status",
                message="Ticket is closed. Cannot register client message."
            )

        self._status = self._status.on_client_message()
        self._set_last_activity(now)

    def register_admin_message(self, now: datetime):
        if self._status.is_closed():
            raise ticket_errors.TicketIsClosedError(
                field="status",
                message="Ticket is closed. Cannot register admin message."
            )

        if self._assigned_admin_id is None:
            raise ticket_errors.AdminIsNotAssignedError(
                field="assigned_admin_id",
                message="Admin is not assigned. Cannot register admin message."
            )

        self._status = self._status.on_admin_message()
        self._set_last_activity(now)

    def _set_last_activity(self, now: datetime):
        self._last_activity_at = now

    def assign_admin(self, admin_id: AdminId):
        if self._status.is_closed():
            raise ticket_errors.TicketIsClosedError(
                field="status",
                message="Ticket is closed. Cannot assign admin."
            )

        if self._assigned_admin_id is not None:
            raise ticket_errors.AdminAlreadyAssignedError(
                field="assigned_admin_id",
                message=f"Admin {self._assigned_admin_id.value} is already assigned to this ticket."
            )

        self._assigned_admin_id = admin_id

    def close(self, *, reason: TicketCloseReason, now: datetime):
        if self._status.is_closed():
            raise ticket_errors.TicketIsClosedError(field="status", message="Ticket is already closed.")

        self._status = self._status.on_close()
        self._close_reason = reason

        self._closed_at = now
        self._set_last_activity(now)

    def _validate(self):
        if self._created_at > self._last_activity_at:
            raise ticket_errors.TicketTimelineError(
                field="last_activity_at",
                message=f"Wrong timeline: created_at <= last_activity_at. "
                        f"Got created_at={self._created_at:{_DT_FMT}}, "
                        f"last_activity_at={self._last_activity_at:{_DT_FMT}}."
            )

        if self._status.is_closed():
            if self._closed_at is None:
                raise ticket_errors.TicketValidationError(
                    field="closed_at",
                    message=f"closed_at is required when status is '{self._status.value}'."
                )
            if self._close_reason is None:
                raise ticket_errors.TicketValidationError(
                    field="close_reason",
                    message=f"close_reason is required when status is '{self._status.value}'."
                )
            if self._last_activity_at > self._closed_at:
                raise ticket_errors.TicketTimelineError(
                    field="closed_at",
                    message=f"Wrong timeline: last_activity_at <= closed_at. "
                            f"Got last_activity_at={self._last_activity_at:{_DT_FMT}}, "
                            f"closed_at={self._closed_at:{_DT_FMT}}."
                )

        else:
            if self._closed_at is not None:
                raise ticket_errors.TicketValidationError(
                    field="closed_at",
                    message=f"closed_at must be None when status is '{self._status.value}'. "
                            f"Got {self._closed_at:{_DT_FMT}}."
                )

            if self._close_reason is not None:
                raise ticket_errors.TicketValidationError(
                    field="close_reason",
                    message=f"close_reason must be None when status is '{self._status.value}'. "
                            f"Got '{self._close_reason}'."
                )
