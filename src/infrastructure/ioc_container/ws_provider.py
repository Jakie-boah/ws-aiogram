from dishka import Provider, Scope, provide

from src.infrastructure.ws.connection import ImplConnectionManager
from src.application.interfaces.ws.connection_manager import ConnectionManager


class WSProvider(Provider):

    @provide(scope=Scope.APP)
    async def get_connection_manager(self) -> ConnectionManager:
        return ImplConnectionManager()
