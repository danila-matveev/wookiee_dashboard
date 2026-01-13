# ARCHITECTURE

## Обзор

Wookiee Dashboard Platform — единая платформа с модульной архитектурой для управления бизнес-процессами, финансов, CRM и AI-агентов.

**Основные принципы**:
- Модульность: Каждый инструмент — независимый модуль
- Единое ядро: Все модули используют общее Core (Company, Employee, Product, etc.)
- Единая аутентификация: Supabase Auth + RLS (Row Level Security)
- Единый AI-провайдер: OpenRouter как основной gateway (с возможностью замены)

## Контекст

Платформа объединяет независимые инструменты (FinManager, Blogger CRM, Telegram AI-assistant и т.д.) на едином корпоративном ядре данных.

**Текущий статус**: Проект находится в процессе миграции к целевой архитектуре. См. `docs/MIGRATION_PLAN.md`.

## Ключевые компоненты

### Слои архитектуры

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

**Подробнее**: См. `docs/PLATFORM_OVERVIEW.md`.

### Корпоративное ядро данных (Core)

Базовая доменная модель (см. `docs/DOMAIN_MODEL.md`):

- **Company/Org** — организации (мульти-компании заложены, но по умолчанию одна)
- **Employee/User** — сотрудники (связь с Supabase Auth)
- **Team/Department** — команды/отделы
- **Role, Permission** — RBAC (роли и права)
- **Product, Category** — продукты/категории
- **Document/File** — документы (Supabase Storage)
- **IntegrationAccount** — аккаунты интеграций (Bitrix24, Telegram и т.д.)
- **Task, CalendarEvent, Reminder** — планирование
- **Agent, AgentRun, AgentLog** — наблюдаемость AI-агентов

## Потоки данных

### Аутентификация

1. Пользователь регистрируется/входит через Supabase Auth
2. Создаётся запись в `core.employees` (триггер)
3. Назначаются роли через `core.employee_roles`
4. RLS политики проверяют права доступа

### Работа с данными

1. App/Module использует Core SDK
2. Core SDK обращается к Supabase (Postgres)
3. RLS политики фильтруют данные по `company_id` и правам пользователя
4. Результат возвращается через Core SDK

### AI-агенты

1. App/Module использует AI Gateway SDK
2. AI Gateway SDK обращается к OpenRouter (или другому провайдеру)
3. Запрос логируется в `core.agent_runs` и `core.agent_logs`
4. Результат возвращается через AI Gateway SDK

**Подробнее**: См. `docs/AGENTS/agents_overview.md`.

## Технологии и зависимости

### Backend/Integrations

- **Python** 3.10+
- **FastAPI** (для API, опционально)
- **Supabase Python client** (`supabase-py`)
- **aiogram** (для Telegram-бота)

### Web Dashboard

- **Next.js** 14+ (App Router)
- **Supabase JS client** (`@supabase/supabase-js`)
- **TypeScript** (рекомендуется)

### AI Gateway

- **Python SDK** с адаптерами для:
  - OpenRouter (рекомендуемый)
  - OpenAI
  - Anthropic
  - Ollama (локальные модели)

### База данных

- **Supabase** (Postgres + Auth + Storage + RLS)
- **Миграции**: Supabase migrations

### Деплой

- **Global Profile**: Vercel (web), Supabase Cloud, OpenRouter
- **RU Profile**: Yandex Cloud (web), self-hosted Supabase, AI-gateway в нейтральном регионе

**Подробнее**: См. `docs/DEPLOYMENT_PROFILES.md`.

## Нефункциональные требования и ограничения

### Безопасность

- Все данные защищены через RLS (Row Level Security)
- Роли и права (RBAC) через `core.roles` и `core.permissions`
- Секреты хранятся в `.env.local` (не коммитятся в git)
- Все интеграции изолированы через `core.integration_accounts`

**Подробнее**: См. `docs/SECURITY_RLS.md`.

### Масштабируемость

- Модульная архитектура позволяет добавлять новые модули без изменения Core
- Мульти-компании заложены (но по умолчанию одна компания)
- Модули могут быть отключены/удалены без разрушения Core

### Наблюдаемость

- Логирование: все действия логируются
- AI-агенты: запуски и логи в `core.agent_runs` и `core.agent_logs`
- Интеграции: синхронизация логируется в `core.integration_sync_logs`

### Профили деплоя

- **Global Profile**: Vercel + Supabase Cloud + OpenRouter
- **RU Profile**: Yandex Cloud + self-hosted Supabase + AI-gateway (нейтральный регион или локальные модели)

**Риски**: Санкции могут заблокировать доступ к Supabase Cloud / OpenRouter из РФ.

**Подробнее**: См. `docs/DEPLOYMENT_PROFILES.md`.

## Roadmap

### Текущий статус

- ✅ Базовая документация и структура
- ✅ Интеграция Bitrix24 (скрипт экспорта сотрудников)
- ✅ Планы Telegram-бота (AI-ассистент)
- ✅ Доменная модель Core
- ✅ RLS стратегия безопасности

### План миграции

Проект находится в процессе миграции к целевой архитектуре.

**Этапы**:
1. **Этап 0**: Стандартизация окружений/секретов/структуры
2. **Этап 1**: Supabase как Core (auth + базовые таблицы + RLS + SDK)
3. **Этап 2**: Перенос Bitrix24 интеграции в `integrations/`
4. **Этап 3**: Telegram bot + базовые AI-агенты
5. **Этап 4**: Web Dashboard + registry модулей + первый модуль (FinManager)

**Подробнее**: См. `docs/MIGRATION_PLAN.md`.

### Следующие шаги

1. Изучить `docs/PLATFORM_OVERVIEW.md` — обзор платформы
2. Выбрать профиль деплоя (`docs/DEPLOYMENT_PROFILES.md`)
3. Настроить окружение (`SECRETS_SETUP.md`)
4. Следовать плану миграции (`docs/MIGRATION_PLAN.md`)

### Новый модуль: wookiee-ai-assistant (Telegram бот)
- Назначение: Telegram-бот для задач/календаря Bitrix24 и дайджестов.
- Архитектурный профиль: FastAPI + aiogram, Supabase (Postgres) для состояния, Bitrix24 входящий вебхук, cron через внешнего провайдера.
- Структура и схема БД: см. `apps/telegram_assistant/README.md` и исходные планы в `wookiee_ai_assistent/`.
- Решения зафиксированы в `ADR.md` (ADR-001).

---

## Дополнительная документация

- **`docs/PLATFORM_OVERVIEW.md`** — детальный обзор платформы
- **`docs/DOMAIN_MODEL.md`** — доменная модель Core (таблицы, связи)
- **`docs/SECURITY_RLS.md`** — безопасность и RLS политики
- **`docs/REPO_STRUCTURE.md`** — структура репозитория (монорепо)
- **`docs/DEPLOYMENT_PROFILES.md`** — профили деплоя (Global vs RU)
- **`docs/MIGRATION_PLAN.md`** — план миграции
- **`docs/AGENTS/agents_overview.md`** — обзор AI-агентов
- **`docs/INTEGRATIONS/bitrix24.md`** — интеграция Bitrix24
