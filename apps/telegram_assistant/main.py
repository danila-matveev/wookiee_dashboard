import logging
import json
import os
import time
from typing import Dict, Optional

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# region agent log
def _agent_log(hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    # Debug-mode NDJSON logger (local runs only). Never log secrets.
    try:
        payload = {
            "sessionId": "debug-session",
            "runId": os.getenv("AGENT_RUN_ID", "pre-fix"),
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000),
        }
        log_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), ".cursor", "debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass
# endregion agent log

# Try to import settings and initialize bot
settings = None
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None
bitrix_client = None
supabase_client = None

try:
    from apps.telegram_assistant.config import settings as _settings
    from apps.telegram_assistant.handlers import (
        register_code,
        register_help,
        register_start,
        register_today,
    )
    from apps.telegram_assistant.handlers.today import build_summary
    from packages.bitrix_client import BitrixClient
    from packages.supabase_db import SupabaseClient
    
    settings = _settings
    _agent_log(
        "H_env_init",
        "apps/telegram_assistant/main.py:init",
        "settings imported",
        {
            "hasTelegramToken": bool(getattr(settings, "telegram_bot_token", None)),
            "hasBitrixWebhook": bool(getattr(settings, "bitrix24_webhook", None)),
            "hasSupabaseUrl": bool(getattr(settings, "supabase_url", None)),
            "hasSupabaseServiceKey": bool(getattr(settings, "supabase_service_role_key", None)),
            "hasCronSecret": bool(getattr(settings, "cron_secret", None)),
        },
    )
    
    # Initialize bot and dependencies
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
    
    logger.info("Bot initialized successfully")
    _agent_log("H_env_init", "apps/telegram_assistant/main.py:init", "bot initialized", {"ok": True})
except Exception as e:
    logger.error("Failed to initialize bot: %s", e, exc_info=True)
    _agent_log("H_env_init", "apps/telegram_assistant/main.py:init", "bot init failed", {"errorType": type(e).__name__})
    # Bot will be None, but app can still serve health endpoint


# Global error handler for aiogram (only if dp is initialized)
if dp is not None:
    @dp.errors()
    async def error_handler(update, exception):
        logger.error("Unhandled error in dispatcher: %s", exception, exc_info=True)
        try:
            if update and update.message:
                await update.message.answer(
                    "Произошла ошибка при обработке команды. Попробуйте позже или используйте /help."
                )
        except Exception:
            pass  # Ignore errors in error handling
        return True

app = FastAPI(title="wookiee-ai-assistant")


@app.on_event("startup")
async def on_startup() -> None:
    logger.info("Telegram assistant started")


@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint that works even if bot is not initialized"""
    status = {
        "status": "ok",
        "bot_initialized": bot is not None and dp is not None,
    }
    _agent_log("H_runtime_requests", "apps/telegram_assistant/main.py:health", "health called", {"botInitialized": status["bot_initialized"]})
    if bot is None or dp is None:
        status["error"] = "Bot not initialized. Check environment variables in Vercel."
        status["required_vars"] = [
            "TELEGRAM_BOT_TOKEN",
            "BITRIX24_WEBHOOK",
            "SUPABASE_URL",
            "SUPABASE_SERVICE_ROLE_KEY",
        ]
    return status


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request) -> Dict[str, str]:
    if bot is None or dp is None:
        logger.error("Bot not initialized - check environment variables")
        _agent_log("H_runtime_requests", "apps/telegram_assistant/main.py:webhook", "webhook rejected (bot not initialized)", {})
        return {"status": "error", "detail": "Bot not initialized. Check environment variables in Vercel."}
    
    body = None
    try:
        body = await request.json()
        logger.info("Received webhook update: %s", body.get("update_id"))
        _agent_log("H_runtime_requests", "apps/telegram_assistant/main.py:webhook", "webhook received", {"hasUpdateId": "update_id" in body})
        update = Update.model_validate(body)
        await dp.feed_update(bot, update)
        logger.info("Update processed successfully")
        _agent_log("H_runtime_requests", "apps/telegram_assistant/main.py:webhook", "webhook processed", {"ok": True})
        return {"status": "processed"}
    except Exception as e:
        logger.error("Error processing webhook: %s", e, exc_info=True)
        _agent_log("H_runtime_requests", "apps/telegram_assistant/main.py:webhook", "webhook error", {"errorType": type(e).__name__})
        # Try to send error message to user if possible
        try:
            if body and "message" in body and bot:
                chat_id = body["message"].get("chat", {}).get("id")
                if chat_id:
                    await bot.send_message(
                        chat_id=chat_id,
                        text="Произошла ошибка при обработке запроса. Попробуйте позже."
                    )
        except Exception:
            pass  # Ignore errors in error handling
        return {"status": "error", "detail": str(e)}


def verify_cron(secret_header: str | None) -> None:
    if settings is None:
        raise HTTPException(status_code=500, detail="Settings not initialized")
    if settings.cron_secret and secret_header != settings.cron_secret:
        raise HTTPException(status_code=401, detail="Invalid CRON secret")


@app.post("/jobs/morning_digest")
async def morning_digest(x_cron_secret: str | None = Header(default=None, alias="X-CRON-SECRET")) -> Dict[str, str]:
    if bot is None or supabase_client is None or bitrix_client is None or settings is None:
        return {"status": "error", "detail": "Bot not initialized. Check environment variables."}
    from apps.telegram_assistant.handlers.today import build_summary
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
    if bot is None or supabase_client is None or bitrix_client is None or settings is None:
        return {"status": "error", "detail": "Bot not initialized. Check environment variables."}
    from apps.telegram_assistant.handlers.today import build_summary
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
