from collections.abc import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.application.interfaces.postgres.uow import UnitOfWork
from src.infrastructure.config.config_storage import Config
from src.infrastructure.postgres.uow import ImplUnitOfWork


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


    @provide(scope=Scope.REQUEST)
    async def get_uow(self, session: AsyncSession) -> UnitOfWork:
        return ImplUnitOfWork(session)
