# Чек-лист подготовок (Supabase-first, личка, email + код через Bitrix `im.notify`)

## Безопасность секретов
**Прочитайте `SECRETS_SETUP.md`** — инструкция по безопасной настройке токенов и ключей.

## 0) Зафиксированные решения MVP

- **Канал работы**: только личка (private chat) в Telegram
- **Связка аккаунтов**: email + подтверждение кодом
- **Инфраструктура**: Supabase-first = **Supabase Postgres + Edge Functions (webhook) + Cron**
- **Bitrix24 доступ**: через **Incoming Webhook**

## Документация
- **Bitrix24 REST API**: https://apidocs.bitrix24.ru/developing-with-rest-api.html

---

## 1) Telegram (1 раз)

- [ ] Создать бота через `@BotFather`
- [ ] Сохранить `TELEGRAM_BOT_TOKEN`
- [ ] Определить username/имя бота (для удобства команды)
- [ ] Решить: бот только для личек (MVP) — **да**

---

## 2) Bitrix24 (1 раз)

### 2.1 Вебхук и права (scopes)

- [ ] Создать отдельного пользователя/интеграцию (рекомендуется) под webhook
- [ ] Создать **Incoming Webhook**
- [ ] Выдать минимальные права (scopes) для MVP:
  - [ ] `user` — поиск пользователя по email (`user.get`)
  - [ ] `task` — задачи (`tasks.task.*`)
  - [ ] `calendar` — календарь (`calendar.event.*`)
  - [ ] `im` — **обязательно** для отправки кода подтверждения (`im.notify`)
- [ ] Сохранить `BITRIX24_WEBHOOK` (полный URL вида `https://<domain>/rest/<user_id>/<token>/`)

### 2.2 Smoke-проверка REST (до разработки)

- [ ] `user.get` — работает
- [ ] `im.notify` — работает (критично для подтверждения кода)
- [ ] `tasks.task.add` — работает (создать тестовую задачу)
- [ ] `calendar.event.add` — работает (создать тестовое событие)

> Если `im.notify` недоступен на тарифе/правах, заранее выбираем fallback:
> - подтверждение через email-OTP (внешняя отправка), или
> - ручная админ-привязка (таблица соответствий).

---

## 3) Supabase (1 раз)

### 3.1 Проект и ключи

- [ ] Создать Supabase Project
- [ ] Зафиксировать регион
- [ ] Подготовить server-side секреты для Edge Functions (Supabase Secrets):
  - [ ] `TELEGRAM_BOT_TOKEN`
  - [ ] `BITRIX24_WEBHOOK`
  - [ ] `DEFAULT_TIMEZONE` (например, `Europe/Moscow`)
  - [ ] `CRON_SECRET` (если будем защищать cron-endpoints)

### 3.2 Таблицы (минимум для MVP)

- [ ] `users` — связь Telegram ↔ Bitrix + настройки уведомлений
  - минимум: `telegram_user_id`, `telegram_chat_id`, `bitrix_user_id`, `email`, `timezone`, `notifications_enabled`, `morning_time`, `evening_time`
- [ ] `auth_codes` — одноразовые коды подтверждения
  - минимум: `telegram_user_id`, `email`, `code_hash`, `expires_at`, `attempts`
- [ ] `notification_outbox` — дедупликация уведомлений (идемпотентность)
  - минимум: `dedupe_key`, `telegram_chat_id`, `payload`, `sent_at`

---

## 4) Контракт команд и сценариев (до кода)

### 4.1 Команды MVP

- [ ] `/start` — регистрация: email → код → подтверждение
- [ ] `/help` — справка
- [ ] `/event` — создать событие (интерактивно)
- [ ] `/schedule today|tomorrow|week` — расписание
- [ ] `/task` — создать задачу (интерактивно)
- [ ] `/tasks today|overdue` — задачи
- [ ] `/notifications` — включить/выключить, задать время

### 4.2 Телемост-ссылка (правило хранения)

- [ ] Сохраняем ссылку в `LOCATION`
- [ ] Дублируем в начале `DESCRIPTION` строкой вида: `[Телемост] <url>`

---

## 5) Cron/уведомления (MVP)

- [ ] `morning_digest` — ежедневно в 08:00 по timezone пользователя:
  - задачи today + overdue
  - события today
- [ ] `evening_digest` — ежедневно в 18:00:
  - итоги дня (опционально)
  - невыполненные today
  - события tomorrow
- [ ] `reminders_tick` — каждые 5 минут:
  - ближайшие события (например, за 15 минут)
  - дедлайны (сегодня/завтра/просрочено)

> Важно: все cron-рассылки должны быть идемпотентными через `notification_outbox`.

---

## 6) Перед тем как “начнем реализацию” (финальная готовность)

- [ ] Есть `TELEGRAM_BOT_TOKEN`
- [ ] Есть `BITRIX24_WEBHOOK` и подтверждено, что `im.notify` доступен
- [ ] Есть Supabase проект и секреты заведены
- [ ] Согласованы команды MVP и расписания уведомлений

