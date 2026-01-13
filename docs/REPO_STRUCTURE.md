# Структура репозитория Wookiee Dashboard Platform

## Обзор

Монорепо с модульной архитектурой. Каждый модуль максимально независим, но использует общее Core.

## Целевая структура

```
wookiee_dashboard/
│
├── apps/                                    # Приложения (точки входа)
│   ├── web-dashboard/                      # Next.js Web Dashboard
│   │   ├── src/
│   │   │   ├── app/                        # Next.js App Router
│   │   │   │   ├── (auth)/
│   │   │   │   │   ├── login/
│   │   │   │   │   └── signup/
│   │   │   │   ├── (dashboard)/
│   │   │   │   │   ├── layout.tsx
│   │   │   │   │   ├── modules/            # Динамические маршруты модулей
│   │   │   │   │   │   └── [module]/
│   │   │   │   │   └── settings/
│   │   │   │   └── api/
│   │   │   ├── components/
│   │   │   ├── lib/
│   │   │   │   └── supabase/               # Supabase client
│   │   │   └── modules/                    # UI компоненты модулей
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── README.md
│   │
│   ├── api/                                # FastAPI BFF (опционально)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routers/
│   │   │   └── middleware/
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── telegram-bot/                       # Python Telegram Bot
│       ├── bot/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── handlers/
│       │   ├── services/
│       │   └── config.py
│       ├── requirements.txt
│       └── README.md
│
├── packages/                                # Общие библиотеки (shared code)
│   ├── core-sdk/                           # Core Domain + Supabase Client
│   │   ├── src/
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py               # Supabase client wrapper
│   │   │   │   ├── models/                 # Domain models
│   │   │   │   │   ├── company.py
│   │   │   │   │   ├── employee.py
│   │   │   │   │   ├── product.py
│   │   │   │   │   └── ...
│   │   │   │   ├── rbac.py                 # RBAC helpers
│   │   │   │   └── errors.py
│   │   │   └── __init__.py
│   │   ├── pyproject.toml                  # или setup.py
│   │   └── README.md
│   │
│   ├── ai-gateway/                         # AI Gateway SDK
│   │   ├── src/
│   │   │   ├── gateway/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py               # AI Gateway client
│   │   │   │   ├── adapters/               # Провайдер-адаптеры
│   │   │   │   │   ├── openrouter.py
│   │   │   │   │   ├── openai.py
│   │   │   │   │   ├── anthropic.py
│   │   │   │   │   └── local.py            # Ollama и т.д.
│   │   │   │   └── types.py
│   │   │   └── __init__.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── integrations/                       # Интеграции SDK
│       ├── src/
│       │   ├── integrations/
│       │   │   ├── __init__.py
│       │   │   ├── base.py                 # Base integration class
│       │   │   ├── bitrix24/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── client.py
│       │   │   │   └── sync.py
│       │   │   └── ...
│       │   └── __init__.py
│       ├── pyproject.toml
│       └── README.md
│
├── modules/                                 # Плагинные модули
│   ├── finmanager/                         # FinManager модуль
│   │   ├── src/
│   │   │   ├── models/                     # Модульные модели
│   │   │   ├── services/                   # Бизнес-логика
│   │   │   ├── api/                        # API endpoints (если нужен)
│   │   │   └── ui/                         # UI компоненты (для web)
│   │   ├── migrations/                     # Миграции модуля
│   │   │   └── 0001_init_finmanager.sql
│   │   ├── manifest.json                   # Реестр модуля
│   │   ├── requirements.txt                # Зависимости модуля
│   │   └── README.md
│   │
│   ├── blogger-crm/                        # Blogger CRM модуль
│   │   ├── src/
│   │   ├── migrations/
│   │   ├── manifest.json
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── telegram-ai/                        # Telegram AI Assistant
│       ├── src/
│       │   ├── handlers/
│       │   ├── agents/
│       │   │   ├── task_assistant.py
│       │   │   └── calendar_assistant.py
│       │   └── services/
│       ├── migrations/
│       ├── manifest.json
│       ├── requirements.txt
│       └── README.md
│
├── infra/                                   # Инфраструктура
│   ├── docker-compose.yml                  # Локальная разработка
│   ├── supabase/
│   │   ├── migrations/                     # Supabase migrations
│   │   │   ├── 00000000000000_init_core.sql
│   │   │   ├── 00000000000001_seed_permissions.sql
│   │   │   ├── 00000000000002_rls_policies.sql
│   │   │   └── ...
│   │   ├── seed.sql                        # Seed данные (опционально)
│   │   └── config.toml                     # Supabase config
│   │
│   ├── deploy/
│   │   ├── global/                         # Global profile
│   │   │   ├── vercel.json
│   │   │   └── env.example
│   │   └── ru/                             # RU profile
│   │       ├── docker-compose.yml
│   │       ├── yandex-cloud/
│   │       └── env.example
│   │
│   └── scripts/
│       ├── setup-dev.sh                    # Настройка dev окружения
│       └── migrate.sh                      # Миграции
│
├── docs/                                    # Документация
│   ├── PLATFORM_OVERVIEW.md                # Обзор платформы
│   ├── DOMAIN_MODEL.md                     # Доменная модель
│   ├── SECURITY_RLS.md                     # Безопасность и RLS
│   ├── REPO_STRUCTURE.md                   # Этот файл
│   ├── DEPLOYMENT_PROFILES.md              # Профили деплоя
│   ├── MIGRATION_PLAN.md                   # План миграции
│   ├── AGENTS/
│   │   └── agents_overview.md              # Обзор агентов
│   └── INTEGRATIONS/
│       └── bitrix24.md                     # Интеграция Bitrix24
│
├── scripts/                                 # Утилиты (корневые скрипты)
│   ├── setup.sh                            # Первоначальная настройка
│   ├── seed-db.sh                          # Seed данных
│   └── export-bitrix24.py                  # Миграция существующего скрипта
│
├── temp/                                    # Временные файлы (gitignore)
│
├── archive/                                 # Архив старых файлов (при необходимости)
│
├── .env.example                            # Корневой шаблон переменных окружения
├── .env.local                              # Локальные переменные (gitignore)
├── .gitignore
├── README.md                               # Главный README
├── ARCHITECTURE.md                         # Обновлённая архитектура
├── ADR.md                                  # Архитектурные решения
├── AGENTS.md                               # Правила работы
├── development-history.md                  # История разработки
└── .CLAUDE-context.md                      # Контекст для AI
```

---

## Описание разделов

### apps/

**Назначение**: Приложения - точки входа пользователей.

**Принципы**:
- Каждое приложение - отдельная папка
- Собственные зависимости (package.json, requirements.txt)
- Собственные конфигурации
- Могут использовать packages/ и modules/

**Приложения**:
1. **web-dashboard** (Next.js) - веб-интерфейс
2. **api** (FastAPI, опционально) - BFF или отдельный API gateway
3. **telegram-bot** (Python) - Telegram бот

---

### packages/

**Назначение**: Общие библиотеки, используемые несколькими приложениями/модулями.

**Принципы**:
- Переиспользуемый код
- Минимальные зависимости
- Четкий API
- Версионирование (опционально, для больших проектов)

**Библиотеки**:
1. **core-sdk** - доступ к Core данным через Supabase
2. **ai-gateway** - единый интерфейс для AI провайдеров
3. **integrations** - SDK для внешних интеграций (Bitrix24, Calendar и т.д.)

---

### modules/

**Назначение**: Плагинные модули - независимые инструменты платформы.

**Принципы**:
- Максимальная независимость
- Собственные зависимости
- Собственные таблицы (схема `modules.<module_name>`)
- Минимальный контракт с Core (только через Core SDK)
- Могут быть отключены/удалены без разрушения Core

**Manifest модуля** (`modules/<module-name>/manifest.json`):
```json
{
  "name": "module-name",
  "description": "Описание модуля",
  "version": "1.0.0",
  "author": "Author Name",
  "routes": ["/modules/module-name"],
  "permissions": ["module:read", "module:write"],
  "features": ["feature-flag-name"],
  "dependencies": {
    "core-sdk": ">=1.0.0"
  }
}
```

**Структура модуля**:
```
modules/<module-name>/
├── src/                      # Код модуля
├── migrations/               # Миграции модуля
├── manifest.json            # Реестр модуля
├── requirements.txt         # Зависимости (Python)
├── package.json             # Зависимости (если есть JS/TS код)
└── README.md                # Документация модуля
```

**Как добавить новый модуль**:
1. Создать папку в `modules/<module-name>/`
2. Добавить `manifest.json`
3. Создать миграции (если нужны таблицы)
4. Использовать Core SDK для доступа к данным
5. Зарегистрировать в web-dashboard (опционально)

---

### infra/

**Назначение**: Инфраструктура, деплой, миграции.

**Структура**:
- `supabase/migrations/` - миграции Core схемы
- `docker-compose.yml` - локальная разработка
- `deploy/` - конфигурации деплоя для разных профилей

---

### docs/

**Назначение**: Вся документация проекта.

**Структура**:
- Корневые документы (обзор, доменная модель, безопасность)
- `AGENTS/` - документация по агентам
- `INTEGRATIONS/` - документация по интеграциям

---

## Миграция текущих файлов

### bitrix24-integration-files/ → integrations/bitrix24/

**План**:
1. Переместить `bitrix24_export.py` → `packages/integrations/src/integrations/bitrix24/client.py`
2. Адаптировать под Core SDK (вместо SQLite → Supabase)
3. Обновить документацию → `docs/INTEGRATIONS/bitrix24.md`

**Временное решение** (до миграции):
- Оставить в `scripts/export-bitrix24.py` как утилиту миграции данных

---

### wookiee_ai_assistent/ → modules/telegram-ai/

**План**:
1. Создать структуру модуля в `modules/telegram-ai/`
2. Перенести документацию/планы в README модуля
3. Реализовать код согласно плану архитектуры

**Временное решение**:
- Оставить документацию как есть, использовать как референс при разработке

---

## Зависимости между компонентами

```
apps/web-dashboard ──┐
                     ├──> packages/core-sdk ──> Supabase
apps/telegram-bot ───┤
                     │
modules/finmanager ──┘
modules/blogger-crm ──> packages/core-sdk
modules/telegram-ai ──> packages/core-sdk
                      └──> packages/ai-gateway ──> OpenRouter/AI providers
                      └──> packages/integrations/bitrix24
```

**Правила**:
- Apps и Modules используют только packages/ (не друг друга напрямую)
- Packages не зависят друг от друга (кроме явных зависимостей)
- Modules не зависят друг от друга

---

## Конфигурация окружений

**Корневой `.env.example`**:
```env
# Deployment Profile
DEPLOYMENT_PROFILE=global  # global или ru

# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# AI Gateway
OPENROUTER_API_KEY=
AI_PROVIDER=openrouter

# Apps
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Environment
ENVIRONMENT=development  # development, staging, production
```

**Локальные переменные** (`.env.local`):
- Создаётся каждым разработчиком локально
- Не коммитится в git
- Может переопределять переменные из `.env.example`

---

## Следующие шаги

1. Изучить `docs/PLATFORM_OVERVIEW.md` - обзор платформы
2. Изучить `docs/DOMAIN_MODEL.md` - доменная модель
3. Изучить `docs/MIGRATION_PLAN.md` - план миграции
4. Начать с Этапа 0 миграции
