from typing import Protocol

from fastapi import WebSocket


class ConnectionManager(Protocol):
    active_connections: dict[int, set[WebSocket]]

    async def connect(self, client_id: int, ws: WebSocket):
        ...

    def disconnect(self, client_id: int, websocket: WebSocket):
        ...

    async def send_personal_message(self, client_id: int, message: str):
        ...
