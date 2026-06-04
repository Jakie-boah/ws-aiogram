from dishka import Provider, Scope, provide

from src.application.interfaces.ws.connection_manager import ConnectionManager
from src.infrastructure.ws.connection import ImplConnectionManager


class WSProvider(Provider):

    @provide(scope=Scope.APP)
    async def get_connection_manager(self) -> ConnectionManager:
        return ImplConnectionManager()
