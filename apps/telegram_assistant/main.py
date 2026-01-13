import logging
from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request

from apps.telegram_assistant.config import settings
from apps.telegram_assistant.handlers import (
    register_code,
    register_help,
    register_start,
    register_today,
)
from apps.telegram_assistant.handlers.today import build_summary
from packages.bitrix_client import BitrixClient
from packages.supabase_db import SupabaseClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=settings.telegram_bot_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

bitrix_client = BitrixClient(settings.bitrix24_webhook)
supabase_client = SupabaseClient(settings.supabase_url, settings.supabase_service_role_key)

# Share dependencies via bot context
bot["bitrix"] = bitrix_client
bot["supabase"] = supabase_client

register_start(dp)
register_help(dp)
register_today(dp, settings.default_timezone)
register_code(dp)

app = FastAPI(title="wookiee-ai-assistant")


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Telegram assistant started")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request) -> Dict[str, str]:
    body = await request.json()
    update = Update.model_validate(body)
    await dp.feed_update(bot, update)
    return {"status": "processed"}


def verify_cron(secret_header: str | None) -> None:
    if settings.cron_secret and secret_header != settings.cron_secret:
        raise HTTPException(status_code=401, detail="Invalid CRON secret")


@app.post("/jobs/morning_digest")
async def morning_digest(x_cron_secret: str | None = Header(default=None, alias="X-CRON-SECRET")) -> Dict[str, str]:
    verify_cron(x_cron_secret)
    users = supabase_client.get_all_users()
    processed = 0
    for user in users:
        try:
            text = await build_summary(supabase_client, bitrix_client, user, settings.default_timezone)
            await bot.send_message(chat_id=user["telegram_chat_id"], text=f"Утренний дайджест:\n\n{text}")
            processed += 1
        except Exception as err:  # noqa: BLE001
            logger.error("Failed to send morning digest for %s: %s", user.get("telegram_id"), err)
    return {"status": "ok", "users_notified": processed}


@app.post("/jobs/evening_digest")
async def evening_digest(x_cron_secret: str | None = Header(default=None, alias="X-CRON-SECRET")) -> Dict[str, str]:
    verify_cron(x_cron_secret)
    users = supabase_client.get_all_users()
    processed = 0
    for user in users:
        try:
            text = await build_summary(supabase_client, bitrix_client, user, settings.default_timezone)
            await bot.send_message(chat_id=user["telegram_chat_id"], text=f"Вечерний дайджест:\n\n{text}")
            processed += 1
        except Exception as err:  # noqa: BLE001
            logger.error("Failed to send evening digest for %s: %s", user.get("telegram_id"), err)
    return {"status": "ok", "users_notified": processed}
