# Профили деплоя Wookiee Dashboard Platform

## Обзор

Платформа поддерживает два профиля деплоя:
1. **Global Profile** - для международных компаний (Vercel + Supabase Cloud + OpenRouter)
2. **RU Profile** - для РФ компаний (Yandex Cloud/self-host + возможный AI-gateway в нейтральном регионе)

## Global Profile (по умолчанию)

### Инфраструктура

- **Web Dashboard**: Vercel (Next.js)
- **База данных**: Supabase Cloud
- **Storage**: Supabase Storage
- **AI Gateway**: OpenRouter API
- **Telegram Bot**: Railway/Render/Vercel Functions (Python)

### Окружения

1. **development** - локальная разработка
   - Supabase: локальный Supabase (Docker)
   - AI: OpenRouter API (dev ключ)
   - Web: `localhost:3000`

2. **staging** - тестовое окружение
   - Supabase: отдельный staging project
   - AI: OpenRouter API (staging ключ)
   - Web: `staging.app.example.com`

3. **production** - продакшен
   - Supabase: production project
   - AI: OpenRouter API (production ключ)
   - Web: `app.example.com`

### Переменные окружения

**Корневой `.env.example` (Global Profile):**

```env
# Deployment Profile
DEPLOYMENT_PROFILE=global
ENVIRONMENT=development  # development, staging, production

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# AI Gateway
OPENROUTER_API_KEY=sk-or-v1-xxx
AI_PROVIDER=openrouter
AI_GATEWAY_URL=https://api.openrouter.ai

# Apps
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Telegram Bot (если используется)
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_WEBHOOK_URL=https://your-app.vercel.app/api/telegram/webhook

# Bitrix24 (если используется)
BITRIX24_WEBHOOK=https://your-domain.bitrix24.ru/rest/1/xxx/

# Logging
LOG_LEVEL=INFO
```

### Локальная разработка

**Docker Compose (`infra/docker-compose.yml`):**

```yaml
version: '3.8'

services:
  supabase:
    image: supabase/postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    volumes:
      - supabase_data:/var/lib/postgresql/data

  # Опционально: локальный Supabase (полный стек)
  # Используйте официальный Supabase CLI для локальной разработки
  # https://supabase.com/docs/guides/cli/local-development

volumes:
  supabase_data:
```

**Запуск локально:**

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd wookiee_dashboard

# 2. Настроить окружение
cp .env.example .env.local
# Заполнить .env.local

# 3. Запустить Supabase локально (через CLI)
supabase start

# 4. Применить миграции
supabase db push

# 5. Запустить Web Dashboard
cd apps/web-dashboard
npm install
npm run dev

# 6. Запустить Telegram Bot (в отдельном терминале)
cd apps/telegram-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

### Деплой на Vercel

**Конфигурация (`apps/web-dashboard/vercel.json`):**

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_SUPABASE_URL": "@supabase_url",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase_anon_key",
    "NEXT_PUBLIC_APP_URL": "@app_url"
  }
}
```

**Переменные окружения в Vercel:**
- `SUPABASE_URL` - из Supabase Dashboard
- `SUPABASE_ANON_KEY` - из Supabase Dashboard
- `SUPABASE_SERVICE_ROLE_KEY` - из Supabase Dashboard (секрет)
- `OPENROUTER_API_KEY` - секрет
- `TELEGRAM_BOT_TOKEN` - секрет (если используется)
- `BITRIX24_WEBHOOK` - секрет (если используется)

### Риски и ограничения

**Риски:**
- ❌ Санкции могут заблокировать доступ к Supabase Cloud / OpenRouter из РФ
- ❌ Зависимость от внешних сервисов (Supabase Cloud, OpenRouter)

**Преимущества:**
- ✅ Простота настройки и поддержки
- ✅ Автоматическое масштабирование
- ✅ Минимальные затраты на инфраструктуру
- ✅ Оптимально для международных компаний

---

## RU Profile (для РФ компаний)

### Инфраструктура

- **Web Dashboard**: Yandex Cloud App Hosting или VM
- **База данных**: Self-hosted Supabase (Postgres) в Yandex Cloud
- **Storage**: Supabase Storage (self-hosted) или Yandex Object Storage
- **AI Gateway**: 
  - Вариант A: AI-gateway в нейтральном регионе (Hetzner/Fly.io) с доступом из РФ
  - Вариант B: Локальные модели (Ollama) или graceful degradation
- **Telegram Bot**: Yandex Cloud Functions или VM

### Окружения

1. **development** - локальная разработка
   - Supabase: локальный Supabase (Docker)
   - AI: OpenRouter API (если доступен) или Ollama локально
   - Web: `localhost:3000`

2. **staging** - тестовое окружение в Yandex Cloud
   - Supabase: staging instance в Yandex Cloud
   - AI: AI-gateway в нейтральном регионе или Ollama
   - Web: `staging.ru.example.com`

3. **production** - продакшен в Yandex Cloud
   - Supabase: production instance в Yandex Cloud
   - AI: AI-gateway в нейтральном регионе или Ollama
   - Web: `app.ru.example.com`

### Переменные окружения

**Корневой `.env.example` (RU Profile):**

```env
# Deployment Profile
DEPLOYMENT_PROFILE=ru
ENVIRONMENT=development  # development, staging, production

# Supabase (self-hosted)
SUPABASE_URL=https://supabase.yandex-cloud.example.com
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# AI Gateway (нейтральный регион или локально)
OPENROUTER_API_KEY=sk-or-v1-xxx  # если доступен
AI_PROVIDER=openrouter  # или "local" для Ollama
AI_GATEWAY_URL=https://ai-gateway.hetzner.example.com  # или http://localhost:11434 для Ollama

# Apps
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Telegram Bot (если используется)
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_WEBHOOK_URL=https://your-app.yandex-cloud.example.com/api/telegram/webhook

# Bitrix24 (если используется)
BITRIX24_WEBHOOK=https://your-domain.bitrix24.ru/rest/1/xxx/

# Logging
LOG_LEVEL=INFO
```

### Self-hosted Supabase в Yandex Cloud

**Варианты:**
1. **VM с Docker Compose** - простой вариант для начала
2. **Yandex Managed PostgreSQL + отдельные сервисы** - более сложный, но гибкий
3. **Kubernetes (Yandex Kubernetes Engine)** - для продакшена

**Минимальный вариант (VM + Docker Compose):**

```yaml
# infra/deploy/ru/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Supabase Auth (Kong + GoTrue)
  # Supabase Storage (Storage API)
  # Supabase Realtime
  # См. официальную документацию Supabase для self-hosting

volumes:
  postgres_data:
```

**Рекомендация**: Используйте официальный Supabase CLI и Kubernetes для продакшена.

**Документация**: https://supabase.com/docs/guides/hosting/overview

### AI Gateway в нейтральном регионе

**Вариант A: Отдельный сервис (Hetzner/Fly.io)**

**Архитектура:**
```
RU (Yandex Cloud)              Neutral Region (Hetzner)
┌─────────────────┐           ┌──────────────────┐
│  Web Dashboard  │──────────>│   AI Gateway     │
│                 │           │  (FastAPI/Python)│
│  Telegram Bot   │──────────>│                  │
│                 │           │  ┌──────────────┐│
└─────────────────┘           │  │ OpenRouter   ││
                              │  │ OpenAI       ││
                              │  │ Anthropic    ││
                              │  └──────────────┘│
                              └──────────────────┘
```

**AI Gateway (`packages/ai-gateway/`):**
- FastAPI сервис
- Проксирует запросы к OpenRouter/OpenAI/Anthropic
- Кэширование, rate limiting
- Логирование

**Деплой:**
- Hetzner Cloud (DE/FI серверы)
- Fly.io (любой регион)
- Railway (любой регион)

**Вариант B: Локальные модели (Ollama)**

**Архитектура:**
```
RU (Yandex Cloud)
┌─────────────────┐
│  Web Dashboard  │
│                 │
│  Telegram Bot   │──────────> Ollama (локально в Yandex Cloud)
│                 │            └─> llama2, mistral, etc.
└─────────────────┘
```

**Ограничения:**
- Меньше возможностей, чем OpenAI/Anthropic
- Требует GPU для хорошей производительности
- Локальные модели могут быть хуже по качеству

### Локальная разработка (RU Profile)

**Docker Compose (`infra/docker-compose.yml`):**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres

  ollama:  # Если используем локальные модели
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
```

**Запуск локально:**

```bash
# Аналогично Global Profile, но:
# 1. AI_GATEWAY_URL=http://localhost:11434 (для Ollama)
# 2. Или AI_GATEWAY_URL=https://ai-gateway.hetzner.example.com (для внешнего gateway)
```

### Деплой на Yandex Cloud

**Вариант 1: App Hosting (для Next.js)**

**Конфигурация (`infra/deploy/ru/yandex-cloud/app.yaml`):**

```yaml
runtime: nodejs18
entrypoint: npm start
env:
  - SUPABASE_URL
  - SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_ROLE_KEY
  - AI_GATEWAY_URL
  - OPENROUTER_API_KEY
```

**Вариант 2: Compute Instance (VM)**

**Запуск через Docker Compose:**
```bash
# На VM
cd /opt/wookiee_dashboard
docker-compose -f infra/deploy/ru/docker-compose.yml up -d
```

### Риски и ограничения

**Риски:**
- ⚠️ Self-hosted Supabase требует дополнительной настройки и поддержки
- ⚠️ AI-запросы могут быть заблокированы (решение: gateway в нейтральном регионе)
- ⚠️ Дополнительные затраты на инфраструктуру (VM, мониторинг, бэкапы)

**Преимущества:**
- ✅ Полный контроль над данными
- ✅ Соответствие требованиям 152-ФЗ (данные в РФ)
- ✅ Нет зависимости от внешних сервисов (кроме AI, если используем внешний gateway)

**Важно**: Все решения должны быть легальными и соответствовать законодательству. Не предлагаем "серые" схемы.

---

## Сравнение профилей

| Критерий | Global Profile | RU Profile |
|----------|---------------|------------|
| **Сложность настройки** | ⭐ Низкая | ⭐⭐⭐ Высокая |
| **Затраты** | Низкие (pay-as-you-go) | Средние/высокие (VM, мониторинг) |
| **Соответствие 152-ФЗ** | ❌ Нет | ✅ Да (данные в РФ) |
| **Зависимость от внешних сервисов** | Высокая | Средняя (только AI gateway) |
| **Контроль над данными** | Ограниченный | Полный |
| **Масштабирование** | Автоматическое | Требует настройки |
| **Риск блокировок** | Высокий (санкции) | Низкий (кроме AI) |

---

## Выбор профиля

**Global Profile рекомендуется для:**
- Международных компаний
- Компаний вне РФ
- Быстрого старта
- MVP/прототипов

**RU Profile рекомендуется для:**
- РФ компаний (требование 152-ФЗ)
- Высоких требований к безопасности данных
- Полного контроля над инфраструктурой

---

## Миграция между профилями

**Важно**: Миграция между профилями требует переноса данных и переконфигурации.

**Шаги миграции:**
1. Экспорт данных из Supabase Cloud
2. Настройка self-hosted Supabase
3. Импорт данных
4. Обновление переменных окружения
5. Переключение DNS/домена

**Документация**: См. `docs/MIGRATION_PLAN.md` для деталей.

---

## Следующие шаги

1. Изучить `docs/PLATFORM_OVERVIEW.md` - обзор платформы
2. Выбрать профиль деплоя
3. Настроить локальное окружение
4. Следовать плану миграции (`docs/MIGRATION_PLAN.md`)
