from dishka import Provider, Scope, provide, from_context

from src.application.interfaces.tg.api import TgAPI
from src.infrastructure.tg.api import ImplTgAPI

from src.infrastructure.config.config_storage import Config
from aiohttp import ClientSession


class TgProvider(Provider):
    context = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_tg_api(self, config: Config, session: ClientSession) -> TgAPI:
        return ImplTgAPI(
            http_session=session,
            chat_id=config.tg_chat_id,
            bot_token=config.bot_token
        )

