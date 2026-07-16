from dataclasses import dataclass

from src.domain.errors.base import AggregateError


@dataclass
class AdminAlreadyAssignedError(AggregateError):
    pass


@dataclass
class AdminIsNotAssignedError(AggregateError):
    pass


@dataclass
class TicketIsClosedError(AggregateError):
    pass


@dataclass
class TicketTimelineError(AggregateError):
    pass


@dataclass
class TicketValidationError(AggregateError):
    pass
