import asyncio

import structlog
from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import make_async_container
from dishka.integrations.aiogram import FromDishka, setup_dishka

from src.infrastructure.config.config_loader import load_config_from_env
from src.infrastructure.ioc_container import LoggerProvider


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(F.reply_to_message)
async def echo_handler(message: Message, logger: FromDishka[structlog.BoundLogger]) -> None:
    try:
        logger.info(message)

        logger.info(message.chat.id)
        logger.info(message.message_id)
        await message.answer(message.text)
    except TypeError:
        await message.answer("Nice try!")


async def main() -> None:
    config = load_config_from_env()
    container = make_async_container(LoggerProvider())

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    setup_dishka(container=container, router=dp, auto_inject=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
