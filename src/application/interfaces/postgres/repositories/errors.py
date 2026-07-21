from dataclasses import dataclass


@dataclass
class PostgresRepositoryError(Exception):
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.field}: {self.message}"


@dataclass
class EntityNotFoundError(PostgresRepositoryError):
    ...


@dataclass
class ActiveTicketAlreadyExistsError(PostgresRepositoryError):
    ...
