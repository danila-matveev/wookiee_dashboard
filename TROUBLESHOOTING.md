# Решение проблем с Telegram ботом на Vercel

## Проблема: Бот не отвечает / Health endpoint не работает

### Шаг 1: Проверка health endpoint

```bash
curl https://wookiee-dashboard.vercel.app/health
```

**Если возвращает `NOT_FOUND`:**
- Деплой не завершился успешно
- Проверьте Vercel Dashboard → Deployments → последний деплой

**Если возвращает JSON с `bot_initialized: false`:**
- Переменные окружения не установлены или неверны
- См. Шаг 2

**Если возвращает `{"status":"ok", "bot_initialized": true}`:**
- Приложение работает, проблема в webhook (см. Шаг 3)

---

### Шаг 2: Настройка переменных окружения в Vercel

1. Откройте [Vercel Dashboard](https://vercel.com/dashboard)
2. Выберите проект `wookiee_dashboard`
3. Перейдите в **Settings → Environment Variables**
4. Добавьте следующие переменные:

#### Обязательные переменные:

```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
BITRIX24_WEBHOOK=https://ваш_домен.bitrix24.ru/rest/1/ваш_webhook/
SUPABASE_URL=https://ваш_проект.supabase.co
SUPABASE_SERVICE_ROLE_KEY=ваш_service_role_ключ
```

#### Опциональные переменные:

```
DEFAULT_TIMEZONE=Europe/Moscow
CRON_SECRET=случайный_секрет_для_cron
APP_BASE_URL=https://wookiee-dashboard.vercel.app
```

5. **ВАЖНО:** После добавления переменных нужно **передеплоить проект**:
   - Vercel Dashboard → Deployments → последний деплой → три точки → **Redeploy**
   - Или сделайте новый коммит и пуш в GitHub

---

### Шаг 3: Проверка после настройки переменных

1. **Проверьте health endpoint:**
   ```bash
   curl https://wookiee-dashboard.vercel.app/health
   ```

   Должен вернуть:
   ```json
   {
     "status": "ok",
     "bot_initialized": true
   }
   ```

2. **Если `bot_initialized: false`, проверьте:**
   - Все переменные установлены в Vercel
   - Проект передеплоен после добавления переменных
   - Проверьте логи: Vercel Dashboard → Deployments → Functions → View Function Logs

---

### Шаг 4: Настройка Telegram Webhook

После того, как health endpoint показывает `bot_initialized: true`:

```bash
# Используйте скрипт
./scripts/setup_telegram_webhook.sh

# Или вручную
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -d "url=https://wookiee-dashboard.vercel.app/webhook/telegram"
```

Проверка webhook:
```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

---

### Шаг 5: Тестирование бота

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте: `/start your@email.com`
4. Проверьте логи в Vercel Dashboard, если бот не отвечает

---

## Частые ошибки и решения

### Ошибка: "Bot not initialized"

**Причина:** Переменные окружения не установлены или проект не передеплоен

**Решение:**
1. Проверьте переменные в Vercel Dashboard → Settings → Environment Variables
2. Передеплойте проект (Redeploy)
3. Проверьте health endpoint снова

### Ошибка: "NOT_FOUND" при обращении к /health

**Причина:** Деплой не завершился успешно или функция не найдена

**Решение:**
1. Проверьте Vercel Dashboard → Deployments → последний деплой
2. Проверьте логи деплоя на наличие ошибок
3. Убедитесь, что `vercel.json` правильный
4. Проверьте, что `requirements.txt` существует в корне

### Ошибка: "ModuleNotFoundError" или "ImportError"

**Причина:** Зависимости не установлены

**Решение:**
1. Убедитесь, что `requirements.txt` в корне проекта
2. Проверьте, что в `requirements.txt` есть строка: `-r apps/telegram_assistant/requirements.txt`
3. Передеплойте проект

### Бот не отвечает, но health endpoint работает

**Причина:** Webhook не настроен или настроен неправильно

**Решение:**
1. Проверьте webhook: `curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"`
2. Убедитесь, что URL правильный: `https://wookiee-dashboard.vercel.app/webhook/telegram`
3. Переустановите webhook: `./scripts/setup_telegram_webhook.sh`

---

## Проверка логов

1. Vercel Dashboard → ваш проект → **Deployments**
2. Последний деплой → **View Function Logs** или **Functions** → `api/index.py` → **Logs**

Ищите:
- `Bot initialized successfully` ✅
- `Received webhook update` ✅
- `ERROR` или `Failed to initialize bot` ❌

---

## Чек-лист для диагностики

- [ ] Health endpoint возвращает JSON (не NOT_FOUND)
- [ ] `bot_initialized: true` в ответе health endpoint
- [ ] Все переменные окружения установлены в Vercel
- [ ] Проект передеплоен после добавления переменных
- [ ] Webhook установлен в Telegram (проверено через `getWebhookInfo`)
- [ ] Логи не показывают ошибок инициализации
- [ ] Бот отвечает на команды в Telegram

---

## Получение значений переменных

### TELEGRAM_BOT_TOKEN
1. Откройте Telegram
2. Найдите [@BotFather](https://t.me/BotFather)
3. Отправьте `/mybots` → выберите вашего бота → **API Token**

### BITRIX24_WEBHOOK
1. Bitrix24 → **Приложения** → **Разработчикам** → **Другие** → **Incoming Webhook**
2. Выберите права: `user`, `user_basic`, `im`, `task`, `calendar`
3. Скопируйте полный URL

### SUPABASE_URL и SUPABASE_SERVICE_ROLE_KEY
1. Supabase Dashboard → ваш проект → **Settings** → **API**
2. **Project URL** → `SUPABASE_URL`
3. **service_role key** (секретный!) → `SUPABASE_SERVICE_ROLE_KEY`

---

## Полезные команды

```bash
# Проверка health
curl https://wookiee-dashboard.vercel.app/health

# Проверка webhook
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"

# Установка webhook
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
  -d "url=https://wookiee-dashboard.vercel.app/webhook/telegram"

# Удаление webhook (если нужно)
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/deleteWebhook"
```
