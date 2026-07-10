from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from typing import ClassVar

from src.domain.errors.ticket_status import (
    CloseReasonValidationError,
    IllegalTicketTransition,
    TicketStatusValidationError,
)
from src.domain.values.base import BaseValueObject


class TicketState(StrEnum):
    OPEN = "open"
    WAITING_ADMIN = "waiting_admin"
    WAITING_CLIENT = "waiting_client"
    CLOSED = "closed"


class TicketEvent(Enum):
    CLIENT_MESSAGE = auto()
    ADMIN_REPLY = auto()
    CLOSE = auto()


class CloseReasonType(StrEnum):
    RESOLVED = "resolved"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class TicketStatus(BaseValueObject):
    value: TicketState

    _TRANSITIONS: ClassVar[dict[tuple[TicketState, TicketEvent], TicketState]] = {
        # ACTION: CLIENT_MESSAGE
        (TicketState.OPEN, TicketEvent.CLIENT_MESSAGE): TicketState.OPEN,
        (TicketState.WAITING_ADMIN, TicketEvent.CLIENT_MESSAGE): TicketState.WAITING_ADMIN,
        (TicketState.WAITING_CLIENT, TicketEvent.CLIENT_MESSAGE): TicketState.WAITING_ADMIN,

        # ACTION: ADMIN_REPLY
        (TicketState.OPEN, TicketEvent.ADMIN_REPLY): TicketState.WAITING_CLIENT,
        (TicketState.WAITING_ADMIN, TicketEvent.ADMIN_REPLY): TicketState.WAITING_CLIENT,
        (TicketState.WAITING_CLIENT, TicketEvent.ADMIN_REPLY): TicketState.WAITING_CLIENT,

        # ACTION: CLOSE
        (TicketState.OPEN, TicketEvent.CLOSE): TicketState.CLOSED,
        (TicketState.WAITING_CLIENT, TicketEvent.CLOSE): TicketState.CLOSED,
        (TicketState.WAITING_ADMIN, TicketEvent.CLOSE): TicketState.CLOSED,

    }

    def validate(self):
        if not isinstance(self.value, TicketState):
            raise TicketStatusValidationError(
                field="ticket_status",
                message=f"Ticket value must be instance of TicketState. Got: {self.value}",
            )

    @classmethod
    def initial(cls) -> "TicketStatus":
        return TicketStatus(TicketState.OPEN)

    def _apply(self, event: TicketEvent) -> "TicketStatus":
        key = (self.value, event)

        if key not in self._TRANSITIONS:
            raise IllegalTicketTransition(
                field="ticket_status",
                message=f"Illegal transition for {self.value} -> {event}."
            )

        return TicketStatus(self._TRANSITIONS[key])

    def on_client_message(self) -> "TicketStatus":
        return self._apply(TicketEvent.CLIENT_MESSAGE)

    def on_admin_message(self) -> "TicketStatus":
        return self._apply(TicketEvent.ADMIN_REPLY)

    def on_close(self) -> "TicketStatus":
        return self._apply(TicketEvent.CLOSE)

    def is_closed(self) -> bool:
        return self.value == TicketState.CLOSED


@dataclass(frozen=True, slots=True)
class CloseReason(BaseValueObject):
    value: CloseReasonType

    def validate(self):
        if not isinstance(self.value, CloseReasonType):
            raise CloseReasonValidationError(
                field="close_reason",
                message=f"Close reason must be instance of CloseReasons. Got: {self.value}",
            )

    @classmethod
    def resolved(cls) -> "CloseReason":
        return CloseReason(CloseReasonType.RESOLVED)

    @classmethod
    def expired(cls) -> "CloseReason":
        return CloseReason(CloseReasonType.EXPIRED)
