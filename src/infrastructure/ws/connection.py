from collections import defaultdict

from fastapi import WebSocket

from src.application.interfaces.ws.connection_manager import ConnectionManager


class ImplConnectionManager(ConnectionManager):
    def __init__(self):
        self.active_connections: dict[int | str, set[WebSocket]] = defaultdict(set)

    async def connect(self, client_id, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id].add(websocket)

    def disconnect(self, client_id, websocket: WebSocket):
        self.active_connections[client_id].discard(websocket)

        if not self.active_connections[client_id]:
            del self.active_connections[client_id]

    async def send_personal_message(self, client_id, message: str):
        for ws in self.active_connections[client_id]:
            await ws.send_text(message)
