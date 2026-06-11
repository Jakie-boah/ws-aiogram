from dishka.integrations.faststream import inject
from faststream.rabbit import (
    ExchangeType,
    RabbitExchange,
    RabbitQueue,
    RabbitRouter,
)
from faststream.rabbit.schemas import Channel


exchange = RabbitExchange("chat", durable=True, type=ExchangeType.DIRECT)

router = RabbitRouter(prefix="")


@router.subscriber(
    channel=Channel(prefetch_count=10),
    exchange=exchange,
    queue=RabbitQueue(
        "client_message_queue",
        durable=True,
        routing_key="client_message",
    ),
    persistent=True,
)
@inject
async def client_message_consumer(

):
    pass

# @router.subscriber()
# @inject
# async def admin_message_consumer():
#     pass
