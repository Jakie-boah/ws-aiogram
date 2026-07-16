from dishka import Provider, Scope, provide, from_context

from src.infrastructure.config.config_storage import Config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from typing import AsyncIterable


class PostgresProvider(Provider):
    config = from_context(Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            config.postgres,
            echo=False,
            pool_size=50,
            max_overflow=50,
            pool_timeout=30,
            pool_pre_ping=True,
        )
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    async def session_poll(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            session_poll: async_sessionmaker,
    ) -> AsyncIterable[AsyncSession]:
        session = session_poll()
        yield session
        await session.close()
