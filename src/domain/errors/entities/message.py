from src.domain.errors.base import AggregateError
from dataclasses import dataclass


@dataclass
class MessageAlreadyDeliveredError(AggregateError):
    pass


@dataclass
class MessageTimelineError(AggregateError):
    pass


@dataclass
class MessageValidationError(AggregateError):
    pass
