from typing import Protocol
from src.domain.values import UserId, Text


class WSGatewayAPI(Protocol):
    async def notify_client(self, *, user_id: UserId, text: Text):
        ...
