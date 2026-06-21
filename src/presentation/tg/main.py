import asyncio

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject, setup_dishka

from src.application.dto.admin_message import AdminMessage
from src.application.use_cases.admin_message_use_case import AdminMessageUseCase
from src.domain.values import MessageId, Text
from src.infrastructure.config.config_loader import load_config_from_env
from src.presentation.dependency_container import create_container


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(F.reply_to_message)
@inject
async def admin_message(
        message: Message,
        use_case: FromDishka[AdminMessageUseCase]
) -> None:
    payload = AdminMessage(
        text=Text(message.text),
        client_message_id=MessageId(message.reply_to_message.message_id)
    )
    await use_case(payload)


async def main() -> None:
    config = load_config_from_env()

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    setup_dishka(container=create_container(config), router=dp, auto_inject=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
