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
)


def create_container(config: Config):
    return make_async_container(
        LoggerProvider(),
        WSProvider(),
        RabbitProvider(),
        TgProvider(),
        AioHttpProvider(),
        RedisProvider(),
        UseCasesProvider(),
        context={Config: config},
    )
