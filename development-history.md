## [2025-12-22 22:43] - Обновление AGENTS.md и базовых файлов

### Что сделано
- Выделен отдельный пункт для ARCHITECTURE.md и добавлен шаблон
- Объединены разделы про архивацию и временные файлы
- Обновлена нумерация и ссылки на разделы
- Созданы базовые файлы ARCHITECTURE.md, ADR.md и .CLAUDE-context.md

### Зачем
Сделать правила более структурированными и выполнить требования по наличию базовой документации.

### Обновлено
- [ ] ARCHITECTURE.md roadmap
- [ ] ADR (если есть)
- [ ] Тесты (если применимо)
- [x] Документация

### Следующие шаги
- При необходимости заполнить ARCHITECTURE.md и ADR.md содержимым

## [2026-01-13 12:15] - Старт wookiee-ai-assistant: архитектура и ADR

### Что сделано
- Прочитал базовые регламенты и существующий план бота (`wookiee_ai_assistent/*`), осмотрел Bitrix24 выгрузку.
- Добавил ADR-001 с решениями по стеку (FastAPI + aiogram, Supabase, Bitrix24 webhook, cron через внешнего провайдера).
- Создал `apps/telegram_assistant/README.md` с архитектурой, env vars и черновиком схемы БД; добавил раздел в `ARCHITECTURE.md`.

### Зачем
Зафиксировать целевой подход для Telegram ассистента в монорепо и подготовить основу для MVP и миграций.

### Обновлено
- [x] ARCHITECTURE.md roadmap
- [x] ADR (если есть)
- [ ] Тесты (если применимо)
- [x] Документация

### Следующие шаги
- Развернуть каркас `apps/telegram_assistant` (FastAPI + aiogram) и подключить `packages/bitrix_client`.
- Подготовить миграции Supabase для схемы `assistant` и RLS.
- Реализовать вертикальный срез: /start, /help, sync задач через Bitrix24 → Supabase → дайджест.

## [2026-01-13 13:00] - Вертикальный срез бота и миграции

### Что сделано
- Добавлен каркас `apps/telegram_assistant` (FastAPI + aiogram): /health, /webhook/telegram, /jobs/morning_digest, команды /start, /help, /today.
- Реализованы минимальные клиенты `packages/bitrix_client` (Bitrix webhook) и `packages/supabase_db` (Supabase schema assistant).
- Добавлена миграция `infra/supabase/migrations/202601131230_assistant_init.sql` с таблицами users/auth_codes/tasks_cache/events_cache/sync_state/notification_outbox.
- Добавлены утилиты для дат и простой юнит-тест `tests/test_dates.py`.

### Зачем
Запуск первого вертикального среза: связать Bitrix24 → Supabase → Telegram-дайджест и подготовить схему хранения.

### Обновлено
- [x] ARCHITECTURE.md roadmap
- [x] ADR (если есть)
- [x] Тесты (минимальный)
- [x] Документация

### Следующие шаги
- Настроить OTP через `im.notify` и полноценный процесс регистрации.
- Добавить RLS и политики доступа для схемы `assistant`.
- Расширить cron-дайджесты и кеширование событий календаря.

## [2026-01-13 14:30] - Деплой на Vercel, OTP, cron и RLS

### Что сделано
- Добавлен `vercel.json`, `api/index.py`, корневой `requirements.txt` для serverless деплоя FastAPI на Vercel.
- Добавлены GitHub Actions cron (`morning_digest`, `evening_digest`) для вызова `/jobs/*` без платного Vercel Cron.
- Реализован OTP через Bitrix `im.notify` (`/start` генерирует код, `/code` подтверждает), расширен дайджест с событиями календаря.
- Cron эндпоинты теперь шлют реальные дайджесты; добавлен кеш событий/задач; расширен Bitrix клиент (im.notify, события).
- Добавлена миграция RLS `202601131400_assistant_rls.sql`; обновлён README приложения.

### Зачем
Обеспечить работающий webhook на Vercel, бесплатный cron через GitHub Actions, безопасную привязку Telegram↔Bitrix с OTP и базовые политики RLS.

### Обновлено
- [x] ARCHITECTURE.md roadmap
- [x] ADR (если есть)
- [x] Тесты (минимальный)
- [x] Документация

### Следующие шаги
- Прогнать деплой на Vercel, проверить `/health` и ответы бота.
- Доработать retry/логирование в cron и добавить кэш календаря по дате/неделе.
- При необходимости усилить RLS (персональные политики под supabase auth, если появится).
