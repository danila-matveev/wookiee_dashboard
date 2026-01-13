# ADR Log

# [2026-01-13 12:00] ADR-001: Архитектура wookiee-ai-assistant (Telegram + Supabase + Bitrix24 webhook)
## Статус
Принято
## Контекст
Нужен Telegram-бот для управления задачами и календарем Bitrix24 с ежедневными/еженедельными дайджестами. Требуется быстрый запуск без сложного OAuth, хранение состояния и синхронизация с Bitrix24, соответствие монорепо-структуре (apps/packages/infra) и стеку Supabase-first.
## Решение
- Язык/стек: Python 3.11+, aiogram 3 + FastAPI webhook endpoint для совместимости с Vercel Cron/GitHub Actions.
- Интеграция Bitrix24: входящий вебхук с выделенным сервисным пользователем; все вызовы через `packages/bitrix_client` с retry и логированием.
- Хранилище: Supabase Postgres (service role в бекенде/cron), базовые таблицы: users (Telegram↔Bitrix), auth_codes, tasks_cache, events_cache, sync_state, notification_outbox.
- Синхронизация: инкрементальная по `last_synced_at` в `sync_state`; хранение внешних `bitrix_id` для задач/событий и checksum/updated_at для идемпотентности.
- Рассылки: ежедневные/еженедельные/overdue через планировщик (Vercel Cron или GitHub Actions) дергают защищенный endpoint (`CRON_SECRET`), который формирует дайджесты и пишет отметки в `notification_outbox`.
- Наблюдаемость: структурные логи (json) в stdout + таблица `agent_logs` (минимум: run_id, user_id, action, status, error).
## Обоснование
- Совпадает с существующим Supabase-first планом в `wookiee_ai_assistent` и общей целевой структурой из `docs/REPO_STRUCTURE.md`.
- Входящий вебхук проще и быстрее OAuth, подходит для приватного ассистента.
- Aiogram + FastAPI закрывают и long-polling (для локали), и webhook (для прод), и позволяют легко навесить healthcheck.
- Cron через внешнего провайдера уменьшает сложность по сравнению с постоянным воркером.
## Последствия
- Нужно безопасно хранить `SUPABASE_SERVICE_ROLE_KEY`, `TELEGRAM_BOT_TOKEN`, `BITRIX24_WEBHOOK`, `CRON_SECRET`.
- Ограничения Bitrix24 по rate limit требуют бэк-оффа и кэширования пользователей.
- RLS для пользовательских таблиц нужно продумать отдельно (часть доступов пойдет через service role).
- Выбор вебхука означает зависимость от стабильности Bitrix24 webhook и необходимости мониторинга ошибок.
## Альтернативы рассмотрены
- OAuth приложение в Bitrix24 — сложнее для MVP, отложено.
- Полностью Supabase Edge Functions вместо FastAPI — ограничивает aiogram и локальную разработку, сложнее для логики бота.
