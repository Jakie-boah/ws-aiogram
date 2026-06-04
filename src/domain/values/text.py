from src.domain.values.base import BaseValueObject
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Text(BaseValueObject):
    value: str

    def validate(self):
        if not self.value.strip():
            raise ValueError("Text cannot be empty")
