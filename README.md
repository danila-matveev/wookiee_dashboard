# Wookiee Dashboard Platform

Единая платформа с модульной архитектурой для управления бизнес-процессами, финансов, CRM и AI-агентов.

## Обзор

Wookiee Dashboard Platform — это монорепо, объединяющий независимые инструменты (FinManager, Blogger CRM, Telegram AI-assistant и т.д.) на едином корпоративном ядре данных.

**Ключевые принципы**:
- **Модульность**: Каждый инструмент — независимый модуль
- **Единое ядро**: Все модули используют общее Core (Company, Employee, Product, etc.)
- **Единая аутентификация**: Supabase Auth + RLS (Row Level Security)
- **Единый AI-провайдер**: OpenRouter как основной gateway (с возможностью замены)

## Структура документации

- **`docs/PLATFORM_OVERVIEW.md`** — обзор платформы и архитектуры
- **`docs/DOMAIN_MODEL.md`** — доменная модель Core (таблицы, связи, RLS)
- **`docs/SECURITY_RLS.md`** — безопасность и RLS политики
- **`docs/REPO_STRUCTURE.md`** — структура репозитория (монорепо)
- **`docs/DEPLOYMENT_PROFILES.md`** — профили деплоя (Global vs RU)
- **`docs/MIGRATION_PLAN.md`** — план миграции текущего репозитория
- **`docs/AGENTS/agents_overview.md`** — обзор AI-агентов
- **`docs/INTEGRATIONS/bitrix24.md`** — интеграция Bitrix24

## Быстрый старт

### Требования

- Python 3.10+
- Node.js 18+ (для Web Dashboard)
- Docker и Docker Compose (для локальной разработки)
- Supabase проект (Cloud или self-hosted)

### Установка

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd wookiee_dashboard

# 2. Настроить окружение
cp .env.example .env.local
# Заполнить .env.local (см. SECRETS_SETUP.md)

# 3. Установить зависимости
# Для Python (backend/integrations)
pip install -r requirements.txt

# Для Node.js (web dashboard)
cd apps/web-dashboard
npm install

# 4. Запустить локально
# Supabase (через CLI)
supabase start

# Применить миграции
supabase db push

# Web Dashboard
cd apps/web-dashboard
npm run dev

# Telegram Bot (в отдельном терминале)
cd apps/telegram-bot
python -m bot.main
```

**Детальная инструкция**: См. `SECRETS_SETUP.md` для настройки секретов и переменных окружения.

## Архитектура

### Слои платформы

```
Apps Layer (web-dashboard, telegram-bot, api)
    ↓
Modules Layer (finmanager, blogger-crm, telegram-ai)
    ↓
Integrations Layer (bitrix24, calendar, etc.)
    ↓
AI Layer (AI Gateway → OpenRouter/OpenAI/Anthropic/Local)
    ↓
Core Layer (Domain + SDK → Supabase)
    ↓
Supabase (Postgres + Auth + Storage)
```

**Подробнее**: См. `docs/PLATFORM_OVERVIEW.md`.

### Корпоративное ядро данных (Core)

Базовая доменная модель включает:
- **Company/Org** — организации
- **Employee/User** — сотрудники (связь с Supabase Auth)
- **Team/Department** — команды/отделы
- **Role, Permission** — RBAC (роли и права)
- **Product, Category** — продукты/категории
- **Document/File** — документы (Supabase Storage)
- **IntegrationAccount** — аккаунты интеграций
- **Task, CalendarEvent, Reminder** — планирование
- **Agent, AgentRun, AgentLog** — наблюдаемость AI-агентов

**Подробнее**: См. `docs/DOMAIN_MODEL.md`.

## Профили деплоя

### Global Profile (по умолчанию)

- **Web**: Vercel (Next.js)
- **База данных**: Supabase Cloud
- **AI**: OpenRouter API
- **Storage**: Supabase Storage

**Риски**: Санкции могут заблокировать доступ к Supabase Cloud / OpenRouter из РФ.

**Подробнее**: См. `docs/DEPLOYMENT_PROFILES.md`.

### RU Profile (для РФ компаний)

- **Web**: Yandex Cloud (App Hosting или VM)
- **База данных**: Self-hosted Supabase (Postgres) в Yandex Cloud
- **AI**: AI-gateway в нейтральном регионе (Hetzner/Fly.io) или локальные модели (Ollama)
- **Storage**: Supabase Storage (self-hosted) или Yandex Object Storage

**Преимущества**: Полный контроль над данными, соответствие 152-ФЗ (данные в РФ).

**Подробнее**: См. `docs/DEPLOYMENT_PROFILES.md`.

## Модульность

### Как добавить новый модуль

1. Создать папку в `modules/<module-name>/`
2. Добавить `manifest.json` (реестр модуля)
3. Создать миграции (если нужны таблицы в схеме `modules.<module_name>`)
4. Использовать Core SDK для доступа к данным
5. Зарегистрировать в web-dashboard (опционально)

**Подробнее**: См. `docs/REPO_STRUCTURE.md`.

## Текущий статус проекта

### Что уже есть

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
5. **Этап 4**: Web Dashboard + registry модулей + первый модуль

**Подробнее**: См. `docs/MIGRATION_PLAN.md`.

## Технологический стек

- **Backend/Integrations**: Python (FastAPI) + Supabase Python client
- **Web Dashboard**: Next.js 14+ (App Router) + Supabase JS client
- **Telegram Bot**: Python (aiogram) + Supabase Python client
- **AI Gateway**: Python SDK (OpenRouter adapter) + адаптеры для разных провайдеров
- **База данных**: Supabase (Postgres + Auth + Storage + RLS)
- **Деплой**: Vercel (Global) / Yandex Cloud (RU)

## Безопасность

- Все данные защищены через RLS (Row Level Security)
- Роли и права (RBAC) через `core.roles` и `core.permissions`
- Секреты хранятся в `.env.local` (не коммитятся в git)
- Все интеграции изолированы через `core.integration_accounts`

**Подробнее**: См. `docs/SECURITY_RLS.md`.

## Разработка

### Правила работы

См. `AGENTS.md` для правил работы над проектом, включая:
- Обновление документации
- ADR (Architecture Decision Records)
- История разработки
- Архивация и временные файлы

### Документация

- `ARCHITECTURE.md` — архитектура проекта (обновляется при значимых изменениях)
- `ADR.md` — архитектурные решения
- `development-history.md` — история разработки

## Лицензия

[Указать лицензию]

## Контакты

[Указать контакты]
