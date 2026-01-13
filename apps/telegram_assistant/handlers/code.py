from datetime import datetime, timezone

from aiogram import Router
from aiogram.types import Message

from apps.telegram_assistant.utils.otp import hash_code, verify_code


def register_code(router: Router) -> None:
    @router.message(commands={"code"})
    async def cmd_code(message: Message) -> None:
        bot = message.bot
        supabase = bot["supabase"]
        bitrix = bot["bitrix"]

        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Укажите код: /code 123456")
            return
        code = parts[1].strip()

        record = supabase.get_auth_code(message.from_user.id, email=None)
        if not record:
            await message.answer("Не найдено ожидающих кодов. Выполните /start <email>.")
            return

        email = record["email"]
        expires_at_str = record.get("expires_at")
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
                if expires_at < datetime.now(timezone.utc):
                    await message.answer("Код истёк. Выполните /start заново.")
                    return
            except Exception:
                pass

        if not verify_code(code, record["code_hash"]):
            await message.answer("Неверный код. Повторите /start для нового кода.")
            return

        bitrix_user = await bitrix.find_user_by_email(email)
        if not bitrix_user:
            await message.answer("Пользователь в Bitrix24 не найден. Проверьте email и выполните /start заново.")
            return

        supabase.upsert_user(
            {
                "telegram_id": message.from_user.id,
                "telegram_chat_id": message.chat.id,
                "bitrix_user_id": int(bitrix_user["ID"]),
                "email": email,
            }
        )
        await message.answer("Привязка завершена. Используйте /today для дайджеста.")
