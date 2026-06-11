from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker

from src.infrastructure.config.config_storage import Config


class RabbitProvider(Provider):
    settings = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_rabbit_broker(self, config: Config) -> RabbitBroker:
        return RabbitBroker(config.rabbit)
