from dishka import make_async_container

from src.infrastructure.config.config_storage import Config
from src.infrastructure.ioc_container import (
    AioHttpProvider,
    LoggerProvider,
    RabbitProvider,
    RedisProvider,
    TgProvider,
    UseCasesProvider,
    WSProvider,
    PostgresProvider,
)


def create_container(config: Config):
    return make_async_container(
        LoggerProvider(),
        PostgresProvider(),
        WSProvider(),
        RabbitProvider(),
        TgProvider(),
        AioHttpProvider(),
        RedisProvider(),
        UseCasesProvider(),
        context={Config: config},
    )
