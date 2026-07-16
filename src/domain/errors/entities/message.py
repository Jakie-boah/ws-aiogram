from dataclasses import dataclass

from src.domain.errors.base import AggregateError


@dataclass
class MessageAlreadyDeliveredError(AggregateError):
    pass


@dataclass
class MessageTimelineError(AggregateError):
    pass


@dataclass
class MessageValidationError(AggregateError):
    pass
