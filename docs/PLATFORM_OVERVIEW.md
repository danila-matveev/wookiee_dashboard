# Wookiee Dashboard Platform - Обзор платформы

## Что сейчас есть в репозитории

### Текущая структура

1. **bitrix24-integration-files/** (`bitrix24-integration-files/`)
   - **Назначение**: Экспорт сотрудников из Bitrix24 в локальную SQLite базу
   - **Технологии**: Python 3.7+, requests, SQLite
   - **Входные точки**: 
     - `bitrix24_export.py` - основной скрипт экспорта
     - `test_webhook.py` - тест подключения к Bitrix24
   - **Конфигурация**: `config.py` (не в git, шаблон `config.py.example`)
   - **Зависимости**: `requirements.txt` (requests==2.31.0)
   - **Статус**: Рабочий скрипт для разовых выгрузок, требует миграции в модульную архитектуру

2. **wookiee_ai_assistent/** (`wookiee_ai_assistent/`)
   - **Назначение**: Планы и документация для Telegram-бота помощника Bitrix24
   - **Архитектурный подход**: Supabase-first (Postgres + Edge Functions + Cron)
   - **Документация**:
     - `README.md` - описание бота
     - `CHECKLIST_PREPARE.md` - чек-лист подготовок
     - `SECRETS_SETUP.md` - настройка секретов
     - `env-template.txt` - шаблон переменных окружения
     - `план_архитектуры_и_структуры_бота-помощника_для_bitrix24_440bcdf6.plan.md` - детальный план
   - **Статус**: Концепция/план, код не реализован

3. **Корневая документация**:
   - `ARCHITECTURE.md` - шаблон (пустой)
   - `ADR.md` - пустой
   - `AGENTS.md` - правила работы над проектом
   - `development-history.md` - история разработки (1 запись)
   - `README.md` - базовый шаблон

### Текущие зависимости

- **Python**: используется в bitrix24-integration-files
- **База данных**: SQLite (локально в bitrix24-integration-files)
- **Внешние сервисы**: Bitrix24 REST API (через webhook)
- **Конфигурация**: локальные файлы (config.py, .env)

---

## Целевая архитектура платформы

### Принципы

1. **Модульность**: Каждый инструмент (FinManager, Blogger CRM, Telegram AI-assistant) - независимый модуль
2. **Единое ядро**: Все модули используют общее корпоративное ядро данных (Company, Employee, Product, etc.)
3. **Единая аутентификация**: Supabase Auth + RLS (Row Level Security)
4. **Единый AI-провайдер**: OpenRouter как основной gateway (с возможностью замены провайдера)
5. **Профили деплоя**: Global (Vercel + Supabase Cloud) и RU (Yandex Cloud/self-host)

### Архитектурные слои

```
┌─────────────────────────────────────────────────────────┐
│                     Apps Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Web Dashboard│  │ Telegram Bot │  │  API/BFF     │  │
│  │  (Next.js)   │  │   (Python)   │  │  (FastAPI)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  Modules Layer                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │FinManager│  │BloggerCRM│  │TelegramAI│  │ ...      ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                 Integrations Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Bitrix24 │  │ Calendar │  │  ...     │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    AI Layer                              │
│  ┌──────────────────────────────────────────┐           │
│  │      AI Gateway (OpenRouter adapter)     │           │
│  │  ┌────────┐  ┌────────┐  ┌────────┐     │           │
│  │  │OpenAI  │  │Claude  │  │Local   │     │           │
│  │  │Adapter │  │Adapter │  │Adapter │     │           │
│  │  └────────┘  └────────┘  └────────┘     │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                     Core Layer                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Core Domain + SDK (Supabase client wrapper)    │   │
│  │  - Company, Employee, Product, Role, Permission │   │
│  │  - Auth, RLS policies, RBAC                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              Supabase (Postgres + Auth + Storage)        │
└─────────────────────────────────────────────────────────┘
```

### Корпоративное ядро данных (Core)

Базовая доменная модель (см. `docs/DOMAIN_MODEL.md`):

- **Company/Org** - организация (мульти-компании заложены, но по умолчанию одна)
- **Employee/User** - профиль сотрудника, связь с `auth.users`
- **Team/Department** - команды/отделы
- **Role, Permission** - RBAC (роли и права)
- **Product, Category/Collection** - продукты/категории
- **Document/File** - документы (связь с Supabase Storage)
- **IntegrationAccount/Source** - аккаунты интеграций (Bitrix24, Telegram и т.д.)
- **Task, Project, CalendarEvent, Reminder** - базовые сущности для планирования
- **Agent, AgentTool/Action, AgentRun, AgentLog** - наблюдаемость AI-агентов

### Модульность

**Как добавить новый модуль:**

1. Создать папку в `modules/<module-name>/`
2. Добавить manifest в `modules/<module-name>/manifest.json`:
   ```json
   {
     "name": "module-name",
     "description": "Описание модуля",
     "version": "1.0.0",
     "routes": ["/module-name"],
     "permissions": ["module:read", "module:write"],
     "features": ["feature-flag-name"]
   }
   ```
3. Использовать Core SDK для доступа к данным
4. При необходимости - создать таблицы в схеме `modules.<module_name>`
5. Зарегистрировать модуль в реестре (опционально, для web dashboard)

**Принцип независимости:**
- Модуль может быть удалён/отключён без разрушения Core
- Модуль использует только Core SDK (не прямые запросы к БД)
- Таблицы модуля в отдельной схеме или с префиксом `module_<name>_*`

---

## Технологический стек (рекомендуемый)

### Рекомендация: Гибридный стек (Python + Next.js)

**Backend/Agents/Integrations:**
- Python (FastAPI) для API, интеграций, Telegram-бота
- Supabase Python client (`supabase-py`) для доступа к данным
- Фоновые jobs: Supabase Edge Functions (Deno) или Celery/RQ (для сложных задач)

**Web Dashboard:**
- Next.js 14+ (App Router) на Vercel
- Supabase JS client для auth и данных
- Server Actions / API Routes для бизнес-логики

**AI Layer:**
- Python SDK для AI-gateway (изолированный слой)
- OpenRouter API как основной провайдер
- Адаптеры для разных провайдеров (OpenAI, Anthropic, локальные модели)

**Почему этот выбор:**
- ✅ Python уже используется в проекте (bitrix24-integration-files)
- ✅ Простота интеграции существующего кода
- ✅ Next.js - современный стек для dashboard'ов
- ✅ Supabase поддерживает оба языка хорошо
- ✅ Разделение ответственности (Python для backend, Next.js для frontend)

**Альтернатива (Fullstack TypeScript):**
- Next.js + отдельный Node.js service для Telegram/Integrations
- Плюсы: единый язык, проще поддержка
- Минусы: требуется переписать Python код, Node.js для Telegram менее популярен

---

## Профили деплоя

### Global Profile (по умолчанию)

**Инфраструктура:**
- **Web**: Vercel (Next.js)
- **База данных**: Supabase Cloud
- **AI**: OpenRouter API
- **Storage**: Supabase Storage

**Окружения:**
- `dev` - локальная разработка
- `staging` - Supabase staging project
- `production` - Supabase production project

**Переменные окружения:**
```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# AI
OPENROUTER_API_KEY=xxx
AI_PROVIDER=openrouter

# Deployment
NEXT_PUBLIC_APP_URL=https://app.example.com
ENVIRONMENT=production
```

**Риски:**
- ❌ Санкции могут заблокировать доступ к Supabase Cloud / OpenRouter из РФ
- ✅ Для международных компаний - оптимальный вариант

### RU Profile (для РФ компаний)

**Инфраструктура:**
- **Web**: Yandex Cloud (App Hosting или VM) или Vercel (если доступен)
- **База данных**: Self-hosted Supabase (Postgres + Auth + Storage) в Yandex Cloud
- **AI**: 
  - Вариант A: AI-gateway в нейтральном регионе (Hetzner/Fly.io) с доступом из РФ
  - Вариант B: Локальные модели (Ollama) или graceful degradation
- **Storage**: Supabase Storage (self-hosted) или Yandex Object Storage

**Окружения:**
- `dev` - локальная разработка
- `staging` - Yandex Cloud staging
- `production` - Yandex Cloud production

**Переменные окружения:**
```env
# Supabase (self-hosted)
SUPABASE_URL=https://supabase.yandex-cloud.example.com
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# AI (нейтральный регион или локально)
OPENROUTER_API_KEY=xxx  # если доступен
AI_PROVIDER=openrouter  # или "local" для Ollama
AI_GATEWAY_URL=https://ai-gateway.hetzner.example.com

# Deployment
NEXT_PUBLIC_APP_URL=https://app.ru.example.com
ENVIRONMENT=production
DEPLOYMENT_PROFILE=ru
```

**Риски и ограничения:**
- ⚠️ Self-hosted Supabase требует дополнительной настройки и поддержки
- ⚠️ AI-запросы могут быть заблокированы (решение: gateway в нейтральном регионе или локальные модели)
- ✅ Полный контроль над данными
- ✅ Соответствие требованиям 152-ФЗ (данные в РФ)

**Важно**: Не предлагаем "серые" схемы. Все решения должны быть легальными и соответствовать законодательству.

---

## Структура репозитория (целевая)

См. детали в `docs/REPO_STRUCTURE.md`.

**Кратко:**
```
wookiee_dashboard/
├── apps/                    # Приложения
│   ├── web-dashboard/       # Next.js dashboard
│   ├── api/                 # FastAPI BFF (опционально)
│   └── telegram-bot/        # Python Telegram bot
├── packages/                # Общие библиотеки
│   ├── core-sdk/            # Core domain + Supabase client
│   ├── ai-gateway/          # AI gateway SDK
│   └── integrations/        # Интеграции (Bitrix24, etc.)
├── modules/                 # Плагинные модули
│   ├── finmanager/          # FinManager модуль
│   ├── blogger-crm/         # Blogger CRM модуль
│   └── telegram-ai/         # Telegram AI assistant
├── infra/                   # Инфраструктура
│   ├── docker-compose.yml   # Локальная разработка
│   ├── supabase/            # Supabase migrations
│   └── deploy/              # Деплой манифесты
├── docs/                    # Документация
├── scripts/                 # Утилиты
└── temp/                    # Временные файлы (gitignore)
```

---

## План миграции

См. детали в `docs/MIGRATION_PLAN.md`.

**Этапы:**

1. **Этап 0**: Стандартизация окружений/секретов/структуры
2. **Этап 1**: Supabase как Core (auth + базовые таблицы + RLS + SDK)
3. **Этап 2**: Перенос Bitrix24 интеграции в `integrations/`
4. **Этап 3**: Telegram bot + базовые AI-агенты
5. **Этап 4**: Web Dashboard + registry модулей + первый модуль (FinManager)

---

## Следующие шаги

1. Изучить `docs/DOMAIN_MODEL.md` - доменная модель Core
2. Изучить `docs/SECURITY_RLS.md` - безопасность и RLS стратегия
3. Изучить `docs/REPO_STRUCTURE.md` - детальная структура репозитория
4. Изучить `docs/DEPLOYMENT_PROFILES.md` - детали деплоя
5. Начать с Этапа 0 миграции
