import asyncio

from dishka.integrations.faststream import setup_dishka as setup_faststream_ioc
from faststream.asgi import AsgiFastStream, make_ping_asgi
from faststream.rabbit import RabbitBroker

from src.infrastructure.config.config_loader import load_config_from_env
from src.presentation.amqp_api.router import router
from src.presentation.dependency_container import create_container


async def application_factory():
    config = load_config_from_env()

    container = create_container(config=config)

    broker = await container.get(RabbitBroker)

    broker.include_routers(router)

    app = AsgiFastStream(
        broker,
        asyncapi_path="/docs",
        asgi_routes=[
            ("/health", make_ping_asgi(broker, timeout=3.0)),
        ],
    )

    setup_faststream_ioc(
        container=container,
        app=app,
        finalize_container=True,
    )
    run_options = {"host": "0.0.0.0", "port": "8003"}

    await app.run(run_extra_options=run_options)


if __name__ == "__main__":
    asyncio.run(application_factory())
