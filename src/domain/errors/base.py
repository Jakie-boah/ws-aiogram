from dataclasses import dataclass


@dataclass
class DomainError(Exception):
    pass


@dataclass
class ValidationError(DomainError):
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.field}: {self.message}"


@dataclass
class AggregateError(DomainError):
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.field}: {self.message}"
