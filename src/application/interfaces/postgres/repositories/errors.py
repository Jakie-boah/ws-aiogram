from dataclasses import dataclass


@dataclass
class PostgresRepositoryError(Exception):
    pass


@dataclass
class EntityNotFoundError(PostgresRepositoryError):
    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.field}: {self.message}"
