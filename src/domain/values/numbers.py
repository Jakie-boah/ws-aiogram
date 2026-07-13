from dataclasses import dataclass

from src.domain.errors import MessageIdValidationError, UserIdValidationError
from src.domain.values.base import BaseValueObject


@dataclass(slots=True, frozen=True)
class MessageIdInt(BaseValueObject):
    """!!! deprecated !!!"""
    value: int

    def validate(self):
        if not isinstance(self.value, int):
            raise MessageIdValidationError(field="message_id", message="Must be an integer")
        if self.value <= 0:
            raise MessageIdValidationError(field="message_id", message="Must be positive")


@dataclass(frozen=True, slots=True)
class UserId(BaseValueObject):
    value: int

    def validate(self):
        if not isinstance(self.value, int):
            raise UserIdValidationError(field="user_id", message="Must be an integer")
        if self.value <= 0:
            raise UserIdValidationError(field="user_id", message="Must be positive")


@dataclass(slots=True, frozen=True)
class ClientId(UserId):
    ...


@dataclass(slots=True, frozen=True)
class AdminId(UserId):
    ...
