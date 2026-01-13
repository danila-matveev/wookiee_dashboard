# Настройка секретов для Wookiee Dashboard Platform

## Безопасность ⚠️

- **НИКОГДА НЕ ОТПРАВЛЯЙТЕ СЕКРЕТЫ В ЧАТ** — они могут остаться в истории или попасть в репозиторий
- **НИКОГДА НЕ КОММИТЬТЕ ФАЙЛЫ С СЕКРЕТАМИ** — они должны быть в `.gitignore`
- Используйте **только локальные файлы** для работы
- Все секреты хранятся в `.env.local` (не коммитится в git)

## Шаг 1: Подготовка файла секретов

1. **Скопируйте шаблон:**
   ```bash
   cp .env.example .env.local
   ```

2. **Заполните своими данными:**
   Откройте `.env.local` и вставьте реальные значения вместо пустых строк.

## Шаг 2: Получение токенов и ключей

### Deployment Profile

Выберите профиль деплоя:
- `DEPLOYMENT_PROFILE=global` — Global Profile (Vercel + Supabase Cloud)
- `DEPLOYMENT_PROFILE=ru` — RU Profile (Yandex Cloud + self-hosted Supabase)

**Подробнее**: См. `docs/DEPLOYMENT_PROFILES.md`.

---

### Supabase

**Global Profile (Supabase Cloud):**

1. Создайте проект на [supabase.com](https://supabase.com)
2. Перейдите в **Settings → API**
3. Скопируйте:
   - **Project URL** → `SUPABASE_URL=`
   - **anon public key** → `SUPABASE_ANON_KEY=`
   - **service_role key** → `SUPABASE_SERVICE_ROLE_KEY=` (НЕ anon key! Только для server-side)

**RU Profile (Self-hosted Supabase):**

1. Настройте self-hosted Supabase (см. `docs/DEPLOYMENT_PROFILES.md`)
2. Скопируйте URL и ключи из вашей установки

**Применение миграций:**

```bash
# Локально
supabase db push

# Или через Supabase Dashboard → SQL Editor
```

**Подробнее**: См. `docs/DOMAIN_MODEL.md` и `docs/SECURITY_RLS.md`.

---

### AI Gateway

**OpenRouter (рекомендуемый):**

1. Создайте аккаунт на [openrouter.ai](https://openrouter.ai)
2. Получите API ключ: **Keys → Create Key**
3. Скопируйте ключ → `OPENROUTER_API_KEY=`

**Настройка:**
```env
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxx
AI_GATEWAY_URL=https://api.openrouter.ai  # по умолчанию
```

**Локальные модели (Ollama, опционально для RU Profile):**

1. Установите Ollama: https://ollama.ai
2. Запустите локально: `ollama serve`
3. Настройка:
```env
AI_PROVIDER=local
AI_GATEWAY_URL=http://localhost:11434
```

**Подробнее**: См. `docs/AGENTS/agents_overview.md` и `docs/DEPLOYMENT_PROFILES.md`.

---

### Telegram Bot (если используется)

1. Напишите в Telegram боту `@BotFather`
2. Команда `/newbot`
3. Введите имя и username бота
4. Сохраните полученный **Bot Token** → `TELEGRAM_BOT_TOKEN=`

**Webhook (для продакшена):**
```env
TELEGRAM_WEBHOOK_URL=https://your-app.example.com/api/telegram/webhook
```

**Подробнее**: См. `docs/AGENTS/agents_overview.md`.

---

### Bitrix24 (если используется)

1. В Bitrix24: **Приложения → Разработчикам → Другие → Incoming Webhook**
2. Выберите права:
   - `user` (обязательно)
   - `user_basic` (рекомендуется)
   - `task` (опционально, для задач)
   - `calendar` (опционально, для календаря)
   - `im` (опционально, для отправки кода подтверждения)
3. Скопируйте **полный URL** webhook'а → `BITRIX24_WEBHOOK=`

**Пример:**
```env
BITRIX24_WEBHOOK=https://your-domain.bitrix24.ru/rest/1/abc123def456/
```

**Хранение в Core:**
После настройки Supabase, webhook'и хранятся в `core.integration_accounts` через Core SDK.

**Подробнее**: См. `docs/INTEGRATIONS/bitrix24.md`.

---

## Шаг 3: Проверка

После заполнения файла `.env.local`:

```bash
# Убедитесь, что файл не коммитится
git status
# .env.local должен быть в списке "Untracked files" или не показываться вообще

# Проверьте, что переменные загружаются
# (для Python)
python -c "from dotenv import load_dotenv; import os; load_dotenv('.env.local'); print(os.getenv('SUPABASE_URL'))"

# (для Node.js)
node -e "require('dotenv').config({path: '.env.local'}); console.log(process.env.SUPABASE_URL)"
```

---

## Шаг 4: Подтверждение

После выполнения настройки секретов:
- Проверьте, что все обязательные переменные заполнены
- Убедитесь, что файл `.env.local` не коммитится в git
- При необходимости — создайте резервную копию `.env.local` в безопасном месте

**Следующий шаг**: См. `docs/MIGRATION_PLAN.md` для плана миграции.

---

## Важные замечания

### Резервные копии

- Сохраните `.env.local` в безопасном месте (не в облаке, если возможно)
- При переустановке ОС/компьютера сможете быстро восстановить
- Не отправляйте файл по email или мессенджерам

### Ротация ключей

- Периодически обновляйте ключи (особенно service_role)
- При компрометации ключа — немедленно создайте новый
- Удалите старый ключ после создания нового

### Разные окружения

- **development** — локальная разработка (`.env.local`)
- **staging** — тестовое окружение (переменные в Vercel/Yandex Cloud)
- **production** — продакшен (переменные в Vercel/Yandex Cloud)

Не используйте production ключи в development окружении!

---

## Шаблон переменных окружения

**Полный шаблон**: См. `.env.example` в корне репозитория.

**Минимальный набор (для начала работы):**

```env
# Deployment Profile
DEPLOYMENT_PROFILE=global  # или ru
ENVIRONMENT=development

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# AI Gateway
OPENROUTER_API_KEY=xxx
AI_PROVIDER=openrouter

# Apps
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Дополнительные переменные** (по необходимости):
- `TELEGRAM_BOT_TOKEN` — для Telegram-бота
- `BITRIX24_WEBHOOK` — для интеграции Bitrix24
- И другие (см. `.env.example`)

---

## Следующий шаг

После настройки секретов:
1. Изучите `docs/PLATFORM_OVERVIEW.md` — обзор платформы
2. Следуйте плану миграции (`docs/MIGRATION_PLAN.md`)
3. Начните с Этапа 0 — стандартизация окружений
