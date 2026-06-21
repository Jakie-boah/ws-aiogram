from collections.abc import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker

from src.application.services.broker.publish import PublisherService
from src.infrastructure.config.config_storage import Config


class RabbitProvider(Provider):
    settings = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_rabbit_broker(self, config: Config) -> AsyncIterable[RabbitBroker]:
        rabbit = RabbitBroker(config.rabbit)
        await rabbit.connect()
        yield rabbit
        await rabbit.close()

    publisher_service = provide(PublisherService, scope=Scope.SESSION)
