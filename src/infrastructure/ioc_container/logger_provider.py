import logging

import structlog
from dishka import Provider, Scope, provide


class LoggerProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_logger(self) -> structlog.BoundLogger:
        logger = structlog.get_logger()

        shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
        ]

        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ]

        structlog.configure(
            processors=processors,  # type: ignore[arg-type]
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )

        return logger  # type: ignore[no-any-return]
