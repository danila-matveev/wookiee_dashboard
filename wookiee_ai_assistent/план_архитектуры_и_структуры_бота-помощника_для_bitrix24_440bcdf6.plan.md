---
name: План архитектуры и структуры бота-помощника для Bitrix24
overview: Детальный план архитектуры, структуры проекта и задач для реализации бота-помощника на базе Bitrix24 REST API. Включает выбор технологий, архитектурные решения, структуру файлов и последовательность реализации.
todos: []
---

# План архитектуры и структуры бота-помощника для Bitrix24

## 0. Актуальный статус и “единственная правда” по решениям (обновлено)

Мы зафиксировали следующий MVP-вариант:

- **Канал**: бот работает **только в личке** (private chat) Telegram.
- **Связка Telegram ↔ Bitrix24**: **по email + подтверждение кодом**, который отправляем пользователю в Bitrix24 через **`im.notify`**.
- **Инфраструктура (лучший вариант)**: **Supabase-first** = **Supabase Postgres + Supabase Edge Functions (webhook) + Supabase Cron**.
- **Надёжность уведомлений**: нужна идемпотентность → используем таблицу outbox (см. `CHECKLIST_PREPARE.md`).

Отдельный чек-лист подготовок лежит тут:

- `Test/Bitrix24/CHECKLIST_PREPARE.md`

> Примечание: ниже по документу остаются более “классические” варианты (Python/SQLite/VPS и т.п.) как справочные. Для текущего MVP ориентируемся на Supabase-first.

## 1. Выбор технологий

### 1.1. Стек технологий (рекомендация)

**Язык программирования:** Python 3.10+

**Библиотеки:**

- **Telegram Bot:** `aiogram 3.x` (современный асинхронный фреймворк для Telegram ботов)
- **HTTP клиент:** `aiohttp` или `httpx` (асинхронные HTTP клиенты)
- **База данных:** `SQLite` (для MVP) или `asyncpg` + PostgreSQL (для продакшена)
- **ORM:** `SQLAlchemy 2.0` с async поддержкой или `Tortoise ORM`
- **Планировщик задач:** `APScheduler` (асинхронный планировщик)
- **Конфигурация:** `pydantic-settings` (валидация конфигурации)
- **Логирование:** `loguru` (удобное логирование)

**Альтернативный стек (Node.js):**

- `Telegraf` + `TypeScript`
- `node-cron` для планировщика
- `Prisma` или `TypeORM` для БД

**Рекомендация:** Python с aiogram для более простой интеграции с существующим кодом в `bitrix24-integration-files`.

### 1.2. База данных

**Вариант 1: SQLite (для MVP)**

- Проще для начала, не требует отдельного сервера
- Достаточно для хранения связи пользователей и настроек уведомлений
- Минусы: ограниченная производительность, проблемы с конкурентным доступом

**Вариант 2: PostgreSQL (для продакшена)**

- Лучшая производительность и масштабируемость
- Поддержка транзакций и конкурентного доступа
- Можно использовать Supabase для упрощения развертывания

**Рекомендация:** Начать с SQLite, предусмотреть возможность миграции на PostgreSQL.

## 2. Архитектура проекта

### 2.1. Структура директорий

```
bitrix24-telegram-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                    # Точка входа бота
│   ├── config.py                  # Конфигурация
│   │
│   ├── handlers/                  # Обработчики команд
│   │   ├── __init__.py
│   │   ├── start.py               # /start, регистрация
│   │   ├── tasks.py               # Команды для задач
│   │   ├── calendar.py            # Команды для календаря
│   │   ├── notifications.py       # Настройка уведомлений
│   │   └── common.py              # Общие команды (/help, ошибки)
│   │
│   ├── services/                  # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── bitrix_client.py       # Клиент для Bitrix24 API
│   │   ├── user_service.py        # Работа с пользователями
│   │   ├── task_service.py        # Работа с задачами
│   │   ├── calendar_service.py    # Работа с календарем
│   │   └── notification_service.py # Уведомления
│   │
│   ├── models/                    # Модели данных
│   │   ├── __init__.py
│   │   ├── database.py            # Настройка БД
│   │   ├── user.py                # Модель пользователя
│   │   └── notification_settings.py # Настройки уведомлений
│   │
│   ├── utils/                     # Утилиты
│   │   ├── __init__.py
│   │   ├── validators.py          # Валидация данных
│   │   ├── formatters.py          # Форматирование сообщений
│   │   ├── parsers.py             # Парсинг дат, пользователей
│   │   └── keyboard.py            # Клавиатуры для бота
│   │
│   ├── schedulers/                # Планировщики задач
│   │   ├── __init__.py
│   │   └── notifications.py       # Планировщик уведомлений
│   │
│   └── middlewares/               # Middleware для бота
│       ├── __init__.py
│       ├── auth.py                # Проверка регистрации
│       └── logging.py             # Логирование запросов
│
├── migrations/                    # Миграции БД (если используем Alembic)
│
├── scripts/                       # Вспомогательные скрипты
│   ├── init_db.py                # Инициализация БД
│   └── test_connection.py        # Тест подключения к Bitrix24
│
├── tests/                         # Тесты
│   ├── __init__.py
│   ├── test_bitrix_client.py
│   └── test_handlers.py
│
├── .env.example                   # Пример файла конфигурации
├── .env                           # Файл конфигурации (не коммитится)
├── .gitignore
├── requirements.txt               # Зависимости Python
├── README.md                      # Документация проекта
├── ARCHITECTURE.md               # Архитектурная документация
└── DEPLOYMENT.md                 # Инструкции по развертыванию
```

### 2.2. Архитектурные компоненты

```mermaid
flowchart TB
    subgraph telegram [Telegram]
        TG_API[Telegram Bot API]
    end
    
    subgraph bot [Bot Application]
        MAIN[main.py<br/>Entry Point]
        HANDLERS[Handlers<br/>Commands Processing]
        SERVICES[Services<br/>Business Logic]
        MIDDLEWARE[Middlewares<br/>Auth, Logging]
    end
    
    subgraph bitrix [Bitrix24]
        BITRIX_API[Bitrix24 REST API]
    end
    
    subgraph storage [Storage]
        DB[(SQLite/PostgreSQL<br/>Users, Settings)]
        CACHE[(Redis Cache<br/>Optional)]
    end
    
    subgraph scheduler [Scheduler]
        APSCHEDULER[APScheduler<br/>Notifications]
    end
    
    TG_API --> MAIN
    MAIN --> MIDDLEWARE
    MIDDLEWARE --> HANDLERS
    HANDLERS --> SERVICES
    
    SERVICES --> BITRIX_API
    SERVICES --> DB
    SERVICES --> CACHE
    
    APSCHEDULER --> SERVICES
    SERVICES --> TG_API
    
    style MAIN fill:#e1f5ff
    style SERVICES fill:#fff4e1
    style DB fill:#e8f5e9
    style BITRIX_API fill:#fce4ec
```

## 3. Модель данных

### 3.1. Таблица users

```sql
CREATE TABLE users (
    telegram_id INTEGER PRIMARY KEY,
    bitrix_id INTEGER NOT NULL,
    bitrix_email TEXT NOT NULL,
    full_name TEXT,
    notification_morning_time TIME DEFAULT '08:00:00',
    notification_evening_time TIME DEFAULT '18:00:00',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_bitrix_id ON users(bitrix_id);
CREATE INDEX idx_users_bitrix_email ON users(bitrix_email);
```

### 3.2. Таблица notification_settings (опционально, если нужны дополнительные настройки)

```sql
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_telegram_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL, -- 'morning', 'evening', 'deadline', 'event'
    enabled BOOLEAN DEFAULT TRUE,
    settings JSON, -- Дополнительные настройки (время, фильтры и т.д.)
    FOREIGN KEY (user_telegram_id) REFERENCES users(telegram_id)
);
```

### 3.3. Таблица cached_data (опционально, для кэширования)

```sql
CREATE TABLE cached_data (
    key TEXT PRIMARY KEY,
    value TEXT, -- JSON строка
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. Архитектура взаимодействия

### 4.1. Поток обработки команды

```
1. Пользователь отправляет команду в Telegram
   ↓
2. Telegram Bot API получает сообщение
   ↓
3. main.py обрабатывает обновление
   ↓
4. Middleware проверяет регистрацию пользователя
   ↓
5. Handler обрабатывает команду
   ↓
6. Service выполняет бизнес-логику
   ↓
7. BitrixClient делает запрос к Bitrix24 API
   ↓
8. Результат форматируется и отправляется пользователю
```

### 4.2. Поток отправки уведомления

```
1. APScheduler срабатывает по расписанию (8:00, 18:00)
   ↓
2. NotificationService получает список пользователей с включенными уведомлениями
   ↓
3. Для каждого пользователя:
   - Запрашивает задачи через BitrixClient
   - Запрашивает события через BitrixClient
   - Форматирует уведомление
   - Отправляет через Telegram Bot API
```

## 5. Основные компоненты

### 5.1. BitrixClient (services/bitrix_client.py)

**Ответственность:**

- Отправка запросов к Bitrix24 REST API
- Обработка ошибок и retry логика
- Кэширование данных где возможно

**Основные методы:**

- `get_users()` — получить список пользователей
- `find_user_by_email(email)` — найти пользователя по email
- `create_task(fields)` — создать задачу
- `get_tasks(filters)` — получить список задач
- `update_task(task_id, fields)` — обновить задачу
- `create_event(fields)` — создать событие
- `get_events(filters)` — получить события
- `update_event(event_id, fields)` — обновить событие

**Особенности:**

- Retry логика с экспоненциальной задержкой
- Обработка ошибок API (QUERY_LIMIT_EXCEEDED, NO_AUTH_FOUND и т.д.)
- Кэширование списка пользователей (TTL: 1 час)

### 5.2. UserService (services/user_service.py)

**Ответственность:**

- Регистрация пользователей (связь Telegram ID ↔ Bitrix ID)
- Получение информации о пользователях
- Управление настройками пользователей

**Основные методы:**

- `register_user(telegram_id, email)` — регистрация по email
- `get_user_by_telegram_id(telegram_id)` — получить пользователя
- `update_notification_settings(telegram_id, settings)` — обновить настройки

### 5.3. TaskService (services/task_service.py)

**Ответственность:**

- Работа с задачами Bitrix24
- Поиск задач по фильтрам
- Форматирование задач для отображения

**Основные методы:**

- `create_task(user_id, title, description, assignee_id, deadline)` — создать задачу
- `get_user_tasks(user_id, filters)` — получить задачи пользователя
- `get_tasks_for_today(user_id)` — задачи на сегодня
- `get_overdue_tasks(user_id)` — просроченные задачи
- `update_task_status(task_id, status)` — обновить статус
- `assign_task(task_id, assignee_id)` — назначить задачу

### 5.4. CalendarService (services/calendar_service.py)

**Ответственность:**

- Работа с календарем Bitrix24
- Создание событий с поддержкой Яндекс Телемост
- Получение событий по фильтрам

**Основные методы:**

- `create_event(user_id, title, description, start_time, end_time, participants, telemost_link)` — создать событие
- `get_events_for_date(user_id, date)` — события на дату
- `get_upcoming_events(user_id, days=7)` — предстоящие события
- `update_event(event_id, fields)` — обновить событие

**Особенности:**

- Ссылка на Яндекс Телемост сохраняется в `LOCATION` и добавляется в `DESCRIPTION` с пометкой "[Телемост]"

### 5.5. NotificationService (services/notification_service.py)

**Ответственность:**

- Формирование и отправка уведомлений
- Получение данных для уведомлений
- Форматирование уведомлений

**Основные методы:**

- `send_morning_notification(user_id)` — утреннее уведомление
- `send_evening_notification(user_id)` — вечернее уведомление
- `send_deadline_reminder(user_id, task_id)` — напоминание о дедлайне
- `send_event_reminder(user_id, event_id)` — напоминание о событии

## 6. Обработка команд (handlers)

### 6.1. Команды для задач

- `/task <title> [description]` — создать задачу (интерактивный диалог)
- `/tasks [my|today|overdue]` — показать задачи
- `/task_status <task_id> <status>` — изменить статус задачи
- `/task_assign <task_id> <user_name>` — переназначить задачу

### 6.2. Команды для календаря

- `/event <title> <start_time> <end_time>` — создать событие (интерактивный диалог)
- `/schedule [today|tomorrow|week]` — показать события
- `/event_update <event_id>` — обновить событие

### 6.3. Общие команды

- `/start` — регистрация/приветствие
- `/help` — справка по командам
- `/notifications` — настройка уведомлений
- `/settings` — настройки профиля

## 7. Планировщик уведомлений (schedulers)

### 7.1. Расписание уведомлений

**Утренние уведомления (8:00):**

- Задачи на сегодня
- События календаря на сегодня
- Просроченные задачи

**Вечерние уведомления (18:00):**

- Завершенные за день задачи
- Невыполненные задачи на сегодня
- События календаря на завтра

**Напоминания о событиях:**

- За 15 минут до события
- За 1 час до события (для важных событий)

**Напоминания о дедлайнах:**

- За 1 день до дедлайна
- В день дедлайна (утром)
- После дедлайна (вечером, если задача не выполнена)

### 7.2. Реализация планировщика

Использовать `APScheduler` с триггерами:

- `CronTrigger` для ежедневных уведомлений
- `IntervalTrigger` для периодических проверок (каждые 5 минут для напоминаний о событиях)

## 8. Конфигурация

### 8.1. Файл .env.example

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Bitrix24
BITRIX24_DOMAIN=your-domain.bitrix24.ru
BITRIX24_WEBHOOK=https://your-domain.bitrix24.ru/rest/1/your_webhook_token/
BITRIX24_USE_WEBHOOK=true

# Database
DATABASE_URL=sqlite:///./bot.db
# Для PostgreSQL: DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Redis (опционально, для кэширования)
REDIS_URL=redis://localhost:6379/0

# Настройки уведомлений
NOTIFICATION_MORNING_TIME=08:00
NOTIFICATION_EVENING_TIME=18:00
EVENT_REMINDER_MINUTES=15

# Логирование
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Настройки Bitrix24 API
BITRIX24_RETRY_ATTEMPTS=3
BITRIX24_RETRY_DELAY=1
BITRIX24_CACHE_TTL=3600
```

## 9. Обработка ошибок

### 9.1. Ошибки Bitrix24 API

- `QUERY_LIMIT_EXCEEDED` — retry с экспоненциальной задержкой
- `NO_AUTH_FOUND` — сообщение об ошибке конфигурации
- `insufficient_scope` — сообщение о недостающих правах доступа
- `user_access_error` — сообщение о том, что пользователь не найден

### 9.2. Ошибки валидации

- Неверный формат даты/времени
- Пользователь не найден в Bitrix24
- Нет доступа к задаче/событию

### 9.3. Ошибки Telegram API

- Retry при временных ошибках
- Логирование ошибок отправки сообщений

## 10. Безопасность

### 10.1. Хранение токенов

- Все токены хранятся в `.env` файле
- `.env` файл добавлен в `.gitignore`
- Никогда не коммитить токены в репозиторий

### 10.2. Валидация данных

- Валидация всех пользовательских вводов
- Проверка формата дат и времени
- Проверка наличия пользователей в Bitrix24

### 10.3. Ограничения доступа

- Проверка регистрации пользователя перед выполнением команд
- Проверка прав доступа в Bitrix24 при работе с данными

## 11. Логирование

### 11.1. Уровни логирования

- `DEBUG` — детальная информация для разработки
- `INFO` — общая информация о работе бота
- `WARNING` — предупреждения (например, пользователь не найден)
- `ERROR` — ошибки, требующие внимания
- `CRITICAL` — критические ошибки

### 11.2. Что логировать

- Все запросы к Bitrix24 API (уровень INFO)
- Ошибки API (уровень ERROR)
- Регистрация пользователей (уровень INFO)
- Отправка уведомлений (уровень INFO)
- Ошибки отправки сообщений (уровень ERROR)

## 12. Тестирование

### 12.1. Типы тестов

- **Unit тесты** — тестирование отдельных функций и методов
- **Integration тесты** — тестирование взаимодействия компонентов
- **E2E тесты** — тестирование полных сценариев использования (опционально)

### 12.2. Что тестировать

- BitrixClient — мокирование запросов к API
- Services — тестирование бизнес-логики
- Handlers — тестирование обработки команд
- Parsers — тестирование парсинга данных

## 13. Деплой и запуск

### 13.1. Локальный запуск

```bash
# 1. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить .env файл
cp .env.example .env
# Отредактировать .env файл с реальными данными

# 4. Инициализировать БД
python scripts/init_db.py

# 5. Запустить бота
python -m bot.main
```

### 13.2. Продакшен деплой

**Вариант 1: VPS с systemd**

- Создать systemd service файл
- Настроить автоматический запуск
- Настроить логирование

**Вариант 2: Docker**

- Создать Dockerfile
- Использовать docker-compose для оркестрации
- Настроить volumes для БД

**Вариант 3: Cloud платформы**

- Heroku, Railway, Render и т.д.
- Настроить переменные окружения
- Настроить автоматический деплой

## 14. Мониторинг и обслуживание

### 14.1. Мониторинг

- Отслеживание ошибок в логах
- Мониторинг использования API (лимиты Bitrix24)
- Мониторинг производительности бота

### 14.2. Обслуживание

- Регулярное обновление зависимостей
- Резервное копирование БД
- Мониторинг использования ресурсов