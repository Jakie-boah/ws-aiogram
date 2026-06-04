from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BaseValueObject(ABC):
    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self): ...
