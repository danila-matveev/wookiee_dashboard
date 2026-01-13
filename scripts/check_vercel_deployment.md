# Инструкция по проверке и настройке Telegram бота после деплоя на Vercel

## Шаг 1: Узнать URL вашего проекта Vercel

1. Откройте [Vercel Dashboard](https://vercel.com/dashboard)
2. Найдите ваш проект `wookiee_dashboard`
3. Перейдите в **Settings → Domains** или посмотрите в **Deployments**
4. URL будет выглядеть как: `https://wookiee-dashboard-xxx.vercel.app` или ваш кастомный домен

**Альтернативно:** URL можно найти в Vercel Dashboard → Project → Settings → Environment Variables, если там установлен `APP_BASE_URL`

---

## Шаг 2: Проверить /health endpoint

### Вариант A: Через браузер
Откройте в браузере: `https://YOUR_VERCEL_URL/health`

Должен вернуться JSON: `{"status":"ok"}`

### Вариант B: Через curl
```bash
curl https://YOUR_VERCEL_URL/health
```

**Ожидаемый результат:**
```json
{"status":"ok"}
```

**Если не работает:**
- Проверьте, что деплой завершился успешно в Vercel Dashboard
- Проверьте логи деплоя: Vercel Dashboard → Deployments → последний деплой → View Function Logs
- Убедитесь, что переменные окружения установлены в Vercel

---

## Шаг 3: Настроить Telegram Webhook

### Вариант A: Использовать скрипт (рекомендуется)

```bash
cd /Users/danilamatveev/Desktop/Документы/Cursor/wookiee_dashboard
./scripts/setup_telegram_webhook.sh
```

Скрипт попросит:
- Токен бота (TELEGRAM_BOT_TOKEN)
- URL проекта Vercel

### Вариант B: Вручную через curl

1. **Узнать токен бота:**
   - Откройте Telegram
   - Найдите бота [@BotFather](https://t.me/BotFather)
   - Отправьте `/mybots` → выберите вашего бота → API Token

2. **Установить webhook:**
   ```bash
   # Замените YOUR_BOT_TOKEN и YOUR_VERCEL_URL
   curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook" \
     -d "url=https://YOUR_VERCEL_URL/webhook/telegram"
   ```

3. **Проверить webhook:**
   ```bash
   curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
   ```

**Ожидаемый результат:**
```json
{
  "ok": true,
  "result": {
    "url": "https://YOUR_VERCEL_URL/webhook/telegram",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## Шаг 4: Протестировать бота

1. **Откройте Telegram**
2. **Найдите вашего бота** (по username, который вы указали при создании)
3. **Отправьте команду:**
   ```
   /start your@email.com
   ```
   (замените `your@email.com` на ваш реальный email из Bitrix24)

4. **Ожидаемое поведение:**
   - Бот должен ответить сообщением о том, что код отправлен в Bitrix24
   - Проверьте Bitrix24 (уведомления в чате) — там должен прийти код подтверждения
   - Отправьте боту: `/code 123456` (замените на реальный код из Bitrix24)
   - Бот должен подтвердить привязку

---

## Шаг 5: Проверить логи (если что-то не работает)

1. Откройте [Vercel Dashboard](https://vercel.com/dashboard)
2. Выберите проект → **Deployments**
3. Выберите последний деплой
4. Нажмите **View Function Logs** или **Functions** → `api/index.py` → **Logs**

**Что искать в логах:**
- `Received webhook update: <update_id>` — webhook получен
- `Update processed successfully` — обработка успешна
- Ошибки (ERROR) — если что-то пошло не так

---

## Частые проблемы

### Бот не отвечает
1. ✅ Проверьте, что `/health` возвращает `{"status":"ok"}`
2. ✅ Проверьте, что webhook установлен правильно (`getWebhookInfo`)
3. ✅ Проверьте логи в Vercel Dashboard
4. ✅ Убедитесь, что все переменные окружения установлены:
   - `TELEGRAM_BOT_TOKEN`
   - `BITRIX24_WEBHOOK`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`

### Ошибка "Invalid CRON secret"
Это нормально для cron endpoints. Они требуют заголовок `X-CRON-SECRET`.

### Webhook не устанавливается
- Проверьте, что URL начинается с `https://`
- Убедитесь, что `/webhook/telegram` endpoint доступен (проверьте через `/health`)
- Проверьте токен бота

### Бот отвечает, но команды не работают
- Проверьте логи в Vercel Dashboard
- Убедитесь, что переменные окружения установлены
- Проверьте, что email существует в Bitrix24

---

## Быстрая проверка всех шагов

```bash
# 1. Проверка health (замените YOUR_VERCEL_URL)
curl https://YOUR_VERCEL_URL/health

# 2. Проверка webhook (замените YOUR_BOT_TOKEN)
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"

# 3. Отправьте боту /start в Telegram
```

---

## Полезные ссылки

- [Vercel Dashboard](https://vercel.com/dashboard)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Vercel Functions Logs](https://vercel.com/docs/functions/logs)
