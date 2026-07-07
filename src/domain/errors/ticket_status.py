from dataclasses import dataclass

from src.domain.errors.base import ValidationError


@dataclass
class TicketStatusValidationError(ValidationError):
    pass


@dataclass
class IllegalTicketTransition(ValidationError):
    pass


@dataclass
class CloseReasonValidationError(ValidationError):
    pass
