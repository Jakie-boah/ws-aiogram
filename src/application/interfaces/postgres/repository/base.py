from abc import abstractmethod
from typing import TypeVar
from typing import Protocol

E = TypeVar("E")
ID = TypeVar("ID")


class Repository[E, ID](Protocol):

    @abstractmethod
    async def save(self, entity: E) -> None:
        ...

    @abstractmethod
    async def get(self, uid: ID) -> E:
        ...
