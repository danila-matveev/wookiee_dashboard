from aiogram import Router
from aiogram.types import Message

from apps.telegram_assistant.utils.otp import expires_at, generate_code, hash_code


def register_start(router: Router) -> None:
    @router.message(commands={"start"})
    async def cmd_start(message: Message) -> None:
        bot = message.bot
        supabase = bot["supabase"]
        bitrix = bot["bitrix"]

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Укажите email: /start your@email")
            return
        email = parts[1].strip()

        user = supabase.get_user_by_telegram_id(message.from_user.id)
        if user:
            await message.answer("Вы уже зарегистрированы. Используйте /today для дайджеста.")
            return

        bitrix_user = await bitrix.find_user_by_email(email)
        if not bitrix_user:
            await message.answer("Не удалось найти пользователя в Bitrix24 по этому email.")
            return

        code = generate_code()
        try:
            await bitrix.send_im_notify(int(bitrix_user["ID"]), f"Код подтверждения Telegram: {code}")
        except Exception:
            await message.answer("Не удалось отправить код через Bitrix24. Проверьте права webhook (im.notify).")
            return

        supabase.insert_auth_code(
            {
                "telegram_id": message.from_user.id,
                "email": email,
                "code_hash": hash_code(code),
                "expires_at": expires_at(),
                "attempts": 0,
            }
        )

        await message.answer("Код отправлен в Bitrix24 (im.notify). Введите /code 123456 чтобы завершить привязку.")
