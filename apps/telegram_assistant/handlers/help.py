from aiogram import Router
from aiogram.types import Message


def register_help(router: Router) -> None:
    @router.message(commands={"help"})
    async def cmd_help(message: Message) -> None:
        await message.answer(
            "Доступные команды:\n"
            "/start <email> — привязать Telegram к Bitrix24 пользователю\n"
            "/today — задачи на сегодня и просроченные\n"
            "/help — помощь"
        )
