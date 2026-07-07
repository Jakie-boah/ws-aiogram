from dataclasses import dataclass

from src.domain.errors import TicketIdValidationError
from src.domain.values.base import BaseValueObject
from uuid import UUID


@dataclass(slots=True, frozen=True)
class TicketId(BaseValueObject):
    value: UUID

    def validate(self):
        if not self.value:
            raise TicketIdValidationError(
                field="ticket_id", message="TicketId is required"
            )
        if not isinstance(self.value, UUID):
            raise TicketIdValidationError(
                field="ticket_id", message="TicketId must be a UUID"
            )
