from collections.abc import AsyncIterable

from aiohttp import ClientSession
from dishka import Provider, Scope, provide


class AioHttpProvider(Provider):

    @provide(scope=Scope.APP)
    async def get_session(self) -> AsyncIterable[ClientSession]:
        async with ClientSession() as session:
            yield session
