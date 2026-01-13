# План миграции Wookiee Dashboard Platform

## Обзор

Поэтапный план миграции текущего репозитория в целевую архитектуру платформы.

**Принципы:**
- Без "сломать всё" - постепенная миграция
- Сохранение работоспособности на каждом этапе
- Возможность отката на каждом этапе

---

## Этап 0: Стандартизация окружений/секретов/структуры

**Цель**: Подготовить инфраструктуру для дальнейшей миграции.

### Что делаем

1. **Создать корневую структуру:**
   ```bash
   mkdir -p apps packages modules infra/supabase/migrations docs/AGENTS docs/INTEGRATIONS scripts temp
   ```

2. **Создать корневой `.env.example`:**
   - Объединить переменные из `bitrix24-integration-files/config.py.example` и `wookiee_ai_assistent/env-template.txt`
   - Добавить переменные для Supabase, AI Gateway, Deployment Profile

3. **Обновить `.gitignore`:**
   - Добавить `.env.local`, `.env.*.local`
   - Добавить `temp/`, `logs/`
   - Стандартизировать исключения

4. **Создать базовый `README.md`:**
   - Описание проекта
   - Быстрый старт
   - Ссылки на документацию

5. **Стандартизировать SECRETS_SETUP.md:**
   - Единый файл для настройки секретов
   - Инструкции для всех интеграций

### Критерии готовности

- [ ] Корневая структура создана
- [ ] `.env.example` создан и заполнен
- [ ] `.gitignore` обновлён
- [ ] `README.md` обновлён
- [ ] `SECRETS_SETUP.md` обновлён
- [ ] Локально можно запустить существующие скрипты (bitrix24-integration-files)

### Как тестируем

```bash
# 1. Склонировать репозиторий
git clone <repo-url>
cd wookiee_dashboard

# 2. Настроить окружение
cp .env.example .env.local
# Заполнить .env.local

# 3. Проверить, что существующие скрипты работают
cd bitrix24-integration-files
python3 test_webhook.py
```

### Риски

- ❌ Минимальные (только структурные изменения)

---

## Этап 1: Supabase как Core (auth + базовые таблицы + RLS + SDK)

**Цель**: Настроить Supabase как корпоративное ядро данных.

### Что делаем

1. **Создать/настроить Supabase проект:**
   - Global: создать проект на supabase.com
   - RU: подготовить self-hosted Supabase (опционально, на этом этапе можно использовать Cloud)

2. **Создать миграции Core:**
   - `infra/supabase/migrations/00000000000000_init_core.sql` - создание схемы `core`
   - `infra/supabase/migrations/00000000000001_seed_permissions.sql` - seed данных (роли, права)
   - `infra/supabase/migrations/00000000000002_rls_policies.sql` - RLS политики

3. **Создать Core SDK (`packages/core-sdk/`):**
   - `src/core/client.py` - Supabase client wrapper
   - `src/core/models/` - Domain models (Company, Employee, Product, etc.)
   - `src/core/rbac.py` - RBAC helpers

4. **Настроить Supabase Auth:**
   - Email/password auth
   - Триггер для создания Employee при регистрации

5. **Создать базовый SDK (`packages/core-sdk/pyproject.toml`):**
   - Зависимости: `supabase-py`, `pydantic`
   - Установка: `pip install -e packages/core-sdk`

### Критерии готовности

- [ ] Supabase проект создан и настроен
- [ ] Миграции применены
- [ ] Core SDK создан и протестирован
- [ ] Можно создать Company и Employee через SDK
- [ ] RLS политики работают (тесты)

### Как тестируем

```bash
# 1. Применить миграции
cd infra/supabase
supabase db push

# 2. Тест Core SDK
cd packages/core-sdk
python -m pytest tests/

# 3. Создать тестовую компанию и сотрудника
python scripts/test_core_sdk.py
```

### Риски

- ⚠️ Миграции могут не примениться (решение: проверить локально сначала)
- ⚠️ RLS политики могут заблокировать доступ (решение: тесты)

---

## Этап 2: Перенос Bitrix24 интеграции в integrations/ + запись данных в Core

**Цель**: Перенести существующую интеграцию Bitrix24 в новую структуру и подключить к Core.

### Что делаем

1. **Создать Integration SDK (`packages/integrations/`):**
   - `src/integrations/base.py` - базовый класс интеграции
   - `src/integrations/bitrix24/client.py` - Bitrix24 client (перенос из `bitrix24_export.py`)
   - `src/integrations/bitrix24/sync.py` - синхронизация данных

2. **Адаптировать под Core SDK:**
   - Вместо SQLite → запись в `core.employees` через Core SDK
   - Вместо локальных таблиц → использовать Core таблицы
   - Создать `core.integration_accounts` для хранения webhook'ов

3. **Создать утилиту миграции (`scripts/export-bitrix24.py`):**
   - Один раз выгрузить данные из Bitrix24 в Core
   - Поддержать инкрементальную синхронизацию (опционально)

4. **Обновить документацию:**
   - `docs/INTEGRATIONS/bitrix24.md` - детальная документация

5. **Архивировать старые файлы:**
   - Переместить `bitrix24-integration-files/` → `archive/2025-01-XX_bitrix24-integration-files/`

### Критерии готовности

- [ ] Integration SDK создан
- [ ] Bitrix24 интеграция работает через Core SDK
- [ ] Можно синхронизировать сотрудников из Bitrix24 в Core
- [ ] Старые файлы архивированы
- [ ] Документация обновлена

### Как тестируем

```bash
# 1. Установить зависимости
pip install -e packages/integrations

# 2. Настроить Bitrix24 webhook в .env.local
BITRIX24_WEBHOOK=https://...

# 3. Запустить синхронизацию
python scripts/export-bitrix24.py

# 4. Проверить данные в Supabase
# (через Supabase Dashboard или SDK)
```

### Риски

- ⚠️ Потеря данных при миграции (решение: резервная копия перед миграцией)
- ⚠️ Несоответствие схем данных (решение: маппинг полей)

---

## Этап 3: Telegram bot + базовые AI-агенты (задачи/календарь) через AI-gateway

**Цель**: Создать Telegram-бота с AI-агентами через единый AI-gateway.

### Что делаем

1. **Создать AI Gateway SDK (`packages/ai-gateway/`):**
   - `src/gateway/client.py` - AI Gateway client
   - `src/gateway/adapters/openrouter.py` - OpenRouter adapter
   - `src/gateway/adapters/local.py` - Ollama adapter (опционально)

2. **Создать Telegram Bot (`apps/telegram-bot/`):**
   - `bot/main.py` - точка входа
   - `bot/handlers/` - обработчики команд
   - `bot/services/` - бизнес-логика
   - Использовать Core SDK для данных
   - Использовать AI Gateway для агентов

3. **Создать базовые AI-агенты:**
   - Task Assistant - создание/управление задачами
   - Calendar Assistant - создание/управление событиями
   - Использовать `core.agents`, `core.agent_runs`, `core.agent_logs`

4. **Настроить деплой Telegram Bot:**
   - Global: Railway/Render/Vercel Functions
   - RU: Yandex Cloud Functions или VM

5. **Обновить документацию:**
   - `docs/AGENTS/agents_overview.md` - обзор агентов

### Критерии готовности

- [ ] AI Gateway SDK создан и протестирован
- [ ] Telegram Bot создан и запущен
- [ ] Базовые команды работают (`/start`, `/task`, `/schedule`)
- [ ] AI-агенты работают (создание задач, событий)
- [ ] Данные сохраняются в Core через Core SDK

### Как тестируем

```bash
# 1. Установить зависимости
pip install -e packages/ai-gateway
pip install -e apps/telegram-bot

# 2. Настроить окружение
TELEGRAM_BOT_TOKEN=xxx
OPENROUTER_API_KEY=xxx

# 3. Запустить бота
cd apps/telegram-bot
python -m bot.main

# 4. Протестировать команды в Telegram
# /start, /task, /schedule, etc.
```

### Риски

- ⚠️ AI-запросы могут не работать (Global: санкции, RU: нужен gateway в нейтральном регионе)
- ⚠️ Telegram Bot может упасть (решение: логирование, мониторинг)

---

## Этап 4: Web Dashboard + registry модулей + первый модуль (FinManager)

**Цель**: Создать веб-интерфейс и показать модульность платформы на примере первого модуля.

### Что делаем

1. **Создать Web Dashboard (`apps/web-dashboard/`):**
   - Next.js 14+ (App Router)
   - Supabase Auth (логин/регистрация)
   - Базовые страницы (dashboard, профиль, настройки)
   - Динамические маршруты для модулей (`/modules/[module]`)

2. **Создать Registry модулей:**
   - Реестр модулей (опционально, можно hardcode на первом этапе)
   - Навигация по модулям
   - Feature flags для модулей

3. **Создать первый модуль (`modules/finmanager/`):**
   - `manifest.json` - реестр модуля
   - `src/` - код модуля
   - `migrations/` - миграции модуля (схема `modules.finmanager_*`)
   - `ui/` - UI компоненты для web dashboard

4. **Интегрировать модуль в Web Dashboard:**
   - Добавить маршрут `/modules/finmanager`
   - Подключить UI компоненты модуля

5. **Настроить деплой Web Dashboard:**
   - Global: Vercel
   - RU: Yandex Cloud App Hosting или VM

### Критерии готовности

- [ ] Web Dashboard создан и деплоится
- [ ] Авторизация работает (Supabase Auth)
- [ ] Можно войти в систему
- [ ] FinManager модуль создан и доступен через `/modules/finmanager`
- [ ] Модуль использует Core SDK

### Как тестируем

```bash
# 1. Установить зависимости
cd apps/web-dashboard
npm install

# 2. Настроить окружение
NEXT_PUBLIC_SUPABASE_URL=xxx
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx

# 3. Запустить локально
npm run dev

# 4. Открыть http://localhost:3000
# 5. Зарегистрироваться/войти
# 6. Перейти в /modules/finmanager
```

### Риски

- ⚠️ Проблемы с авторизацией (решение: тесты, логирование)
- ⚠️ Модуль может не загрузиться (решение: обработка ошибок)

---

## Общие рекомендации

### Резервные копии

**Перед каждым этапом:**
1. Создать резервную копию базы данных (если есть)
2. Закоммитить текущее состояние в git
3. Создать ветку для этапа (опционально)

### Тестирование

**На каждом этапе:**
1. Юнит-тесты для нового кода
2. Интеграционные тесты для API/интеграций
3. Ручное тестирование критических сценариев

### Документация

**После каждого этапа:**
1. Обновить `development-history.md`
2. Обновить `ARCHITECTURE.md` (если архитектура изменилась)
3. Добавить ADR (если принято важное решение)

---

## Временные файлы и архивация

### bitrix24-integration-files/

**Статус**: Рабочий код, требует миграции на Этапе 2.

**Действия:**
- На Этапе 0-1: оставить как есть
- На Этапе 2: архивировать после миграции

### wookiee_ai_assistent/

**Статус**: Документация/планы, используется на Этапе 3.

**Действия:**
- На Этапе 0-2: оставить как есть
- На Этапе 3: использовать как референс, можно архивировать после реализации

---

## Следующие шаги

1. Начать с Этапа 0 (стандартизация)
2. По завершении каждого этапа - зафиксировать в `development-history.md`
3. При необходимости - откатиться на предыдущий этап

---

## Оценка времени

**Примерная оценка:**
- Этап 0: 1-2 дня
- Этап 1: 3-5 дней
- Этап 2: 2-3 дня
- Этап 3: 5-7 дней
- Этап 4: 7-10 дней

**Итого**: ~3-4 недели (в зависимости от опыта и сложности модулей)
