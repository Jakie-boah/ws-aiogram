from src.domain.errors.base import AggregateError
from dataclasses import dataclass


@dataclass
class AdminAlreadyAssignedError(AggregateError):
    pass


@dataclass
class AdminIsNotAssignedError(AggregateError):
    pass


@dataclass
class TicketIsClosedError(AggregateError):
    pass
