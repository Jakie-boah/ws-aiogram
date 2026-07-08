from dataclasses import dataclass
from uuid import UUID, uuid4

from src.domain.errors import TicketIdValidationError
from src.domain.values.base import BaseValueObject


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

    @classmethod
    def new(cls):
        return cls(value=uuid4())
