from dataclasses import dataclass

from src.domain.errors.base import ValidationError


@dataclass
class TextValidationError(ValidationError):
    pass
