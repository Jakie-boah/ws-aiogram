from dishka import make_async_container

from src.infrastructure.config.config_storage import Config
from src.infrastructure.ioc_container import AioHttpProvider, LoggerProvider, TgProvider, WSProvider


def create_container(config: Config):
    return make_async_container(
        LoggerProvider(),
        WSProvider(),
        TgProvider(),
        AioHttpProvider(),
        context={Config: config},
    )
