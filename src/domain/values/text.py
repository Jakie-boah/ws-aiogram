from dataclasses import dataclass

from src.domain.errors import TextValidationError
from src.domain.values.base import BaseValueObject


@dataclass(frozen=True, slots=True)
class Text(BaseValueObject):
    value: str

    def validate(self):
        if not self.value.strip():
            raise TextValidationError(field="text", message="Cannot be empty")
