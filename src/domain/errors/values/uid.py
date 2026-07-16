from dataclasses import dataclass

from src.domain.errors.base import ValidationError


@dataclass
class TicketIdValidationError(ValidationError):
    pass


@dataclass
class MessageIdValidationError(ValidationError):
    pass
