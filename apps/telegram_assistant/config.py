from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    bitrix24_webhook: str = Field(..., alias="BITRIX24_WEBHOOK")
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(..., alias="SUPABASE_SERVICE_ROLE_KEY")
    default_timezone: str = Field("Europe/Moscow", alias="DEFAULT_TIMEZONE")
    cron_secret: str | None = Field(None, alias="CRON_SECRET")
    app_base_url: str | None = Field(None, alias="APP_BASE_URL")
    openrouter_api_key: str | None = Field(None, alias="OPENROUTER_API_KEY")
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
