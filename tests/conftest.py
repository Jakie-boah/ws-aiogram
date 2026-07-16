import pytest
import structlog


@pytest.fixture(autouse=True, name="logger", scope="session")
def logger_setup():
    logger = structlog.get_logger()

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=True),
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
    ]
    processors = [
        *shared_processors,
        structlog.dev.ConsoleRenderer(colors=True, exception_formatter=structlog.dev.plain_traceback),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    return logger


pytest_plugins = [
    "tests.fixtures.config",
    "tests.fixtures.ioc_container",
    "tests.fixtures.postgres",
]
