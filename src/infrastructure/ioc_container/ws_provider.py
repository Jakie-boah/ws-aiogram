import structlog
from dishka import Provider, Scope, provide

from src.application.interfaces.ws.connection_manager import ConnectionManager
from src.infrastructure.ws.connection import ImplConnectionManager
from src.application.interfaces.ws.gateway import WSGatewayAPI
from src.infrastructure.ws.gateway import ImplWSGatewayAPI

from src.infrastructure.config.config_storage import Config
from aiohttp import ClientSession


class WSProvider(Provider):
    impl_connection_manager = provide(ImplConnectionManager, scope=Scope.APP, provides=ConnectionManager)

    @provide(scope=Scope.APP)
    async def get_ws_gateway(
            self,
            config: Config,
            logger: structlog.BoundLogger,
            session: ClientSession,
    ) -> WSGatewayAPI:

        return ImplWSGatewayAPI(
            internal_token=config.internal_token,
            gateway=f"http://{config.ws_host}:{config.ws_port}/internal/ws",
            logger=logger,
            session=session
        )
