# Анализ сессии отладки: Проблемы с деплоем на Vercel

**Дата:** 2026-01-13  
**Проект:** wookiee-dashboard (Telegram бот на FastAPI + aiogram)  
**Платформа:** Vercel (Python serverless functions)

---

## Краткое резюме проблемы

**Главная проблема:** Проект не работает на Vercel после деплоя. Билд успешен, но приложение возвращает 404 или Internal Server Error. Последняя ошибка билда: `The pattern "api/index.py" defined in functions doesn't match any Serverless Functions inside the api directory.`

**Статус:** ❌ Не решено

---

## Хронология проблем и попыток решения

### 1. Исходная проблема (начало сессии)
- **Симптом:** Проект не работает, редиплой не помог, переменные окружения проверены
- **Действия:** Начата диагностика с нуля

### 2. Проблема #1: Невалидный `runtime` в `vercel.json`
- **Ошибка билда:** `Function Runtimes must have a valid version, for example now-php@1.0.0`
- **Причина:** В `vercel.json` было указано `"runtime": "python3.10"`, что невалидно для Vercel
- **Решение:** Убрали поле `runtime` из `vercel.json`
- **Коммит:** `2b5ba89` - "fix(vercel): убрать невалидный runtime + добавить диагностику"
- **Результат:** ✅ Билд прошёл, но появилась следующая проблема

### 3. Проблема #2: Конфликт версий зависимостей Python

#### 3.1. Конфликт `pydantic`
- **Ошибка билда:** `aiogram==3.4.1 depends on pydantic>=2.4.1,<2.6` но проект требует `pydantic==2.6.3`
- **Решение:** Понизили `pydantic` с `2.6.3` до `2.5.3`
- **Коммит:** `5d8b290` - "fix(deps): понизить pydantic до 2.5.3 для совместимости с aiogram 3.4.1"

#### 3.2. Конфликт `httpx`
- **Ошибка билда:** `supabase==2.4.0 depends on httpx>=0.24,<0.26` но проект требует `httpx==0.26.0`
- **Решение:** Понизили `httpx` с `0.26.0` до `0.25.2`
- **Коммит:** `8d0316f` - "fix(deps): понизить httpx до 0.25.2 для совместимости с supabase 2.4.0"
- **Результат:** ✅ Билд прошёл успешно

### 4. Проблема #3: Роутинг и Runtime ошибки

#### 4.1. Замена `routes` на `rewrites`
- **Проблема:** Изначально использовались `routes` в `vercel.json`
- **Решение:** Заменили `routes` на `rewrites` (правильный формат для Vercel)
- **Коммит:** `c271ac5` - "fix(vercel): заменить routes на rewrites для Python функций"
- **Результат:** ❌ Не помогло, проблема осталась

#### 4.2. Runtime ошибки
- **Симптом:** После успешного билда приложение возвращает:
  - 404 на корневом пути `/`
  - Internal Server Error на `/health`
  - Нет логов в Vercel Dashboard → Logs
- **Попытка решения:** Добавили подробное логирование в stdout
- **Коммит:** `4835f23` - "feat: добавить подробное логирование для диагностики рантайм-ошибок на Vercel"
- **Результат:** ❌ Появилась новая ошибка билда

### 5. Проблема #4: Vercel не находит serverless функцию (текущая)
- **Ошибка билда:** `The pattern "api/index.py" defined in functions doesn't match any Serverless Functions inside the api directory.`
- **Коммит:** `4835f23` (последний)
- **Статус:** ❌ Критическая ошибка, билд падает

---

## Структура проекта

```
wookiee_dashboard/
├── api/
│   └── index.py                    # Точка входа для Vercel (импортирует app из apps/telegram_assistant/main.py)
├── apps/
│   └── telegram_assistant/
│       ├── main.py                 # FastAPI приложение
│       ├── config.py
│       ├── handlers/
│       └── requirements.txt
├── packages/
│   ├── bitrix_client/
│   └── supabase_db/
├── vercel.json                     # Конфигурация Vercel
└── requirements.txt                # Ссылается на apps/telegram_assistant/requirements.txt
```

---

## Текущая конфигурация `vercel.json`

```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 10
    }
  },
  "rewrites": [
    { "source": "/health", "destination": "/api/index.py" },
    { "source": "/webhook/telegram", "destination": "/api/index.py" },
    { "source": "/jobs/morning_digest", "destination": "/api/index.py" },
    { "source": "/jobs/evening_digest", "destination": "/api/index.py" }
  ]
}
```

---

## Зависимости (после всех исправлений)

**apps/telegram_assistant/requirements.txt:**
- `fastapi==0.110.0`
- `uvicorn[standard]==0.27.1`
- `aiogram==3.4.1`
- `httpx==0.25.2` (понижено с 0.26.0)
- `pydantic==2.5.3` (понижено с 2.6.3)
- `pydantic-settings==2.2.1`
- `supabase==2.4.0`
- `python-dateutil==2.8.2`
- `python-dotenv==1.0.1`

---

## Коммиты в сессии

1. `2b5ba89` - fix(vercel): убрать невалидный runtime + добавить диагностику
2. `c271ac5` - fix(vercel): заменить routes на rewrites для Python функций
3. `2fa4041` - chore: trigger Vercel redeploy (пустой коммит)
4. `5d8b290` - fix(deps): понизить pydantic до 2.5.3 для совместимости с aiogram 3.4.1
5. `8d0316f` - fix(deps): понизить httpx до 0.25.2 для совместимости с supabase 2.4.0
6. `4835f23` - feat: добавить подробное логирование для диагностики рантайм-ошибок на Vercel ❌ (ошибка билда)

---

## Ключевые наблюдения

1. **Vercel не подхватывает автоматически новые коммиты** - приходилось делать redeploy вручную
2. **Конфликты зависимостей решены** - все зависимости совместимы
3. **Проблема в конфигурации Vercel** - последняя ошибка указывает, что Vercel не распознаёт `api/index.py` как serverless функцию
4. **Отсутствие Runtime логов** - даже после успешного билда логи не появляются в Vercel Dashboard → Logs

---

## Возможные причины проблемы

### Гипотеза 1: Неправильная структура для Python serverless функций на Vercel
- Для Python на Vercel может требоваться другой формат конфигурации
- Возможно, нужно использовать другой подход (не через `api/index.py`, а через другую структуру)

### Гипотеза 2: FastAPI + Vercel несовместимость
- FastAPI может требовать специальной настройки для работы на Vercel
- Возможно, нужен адаптер или другой способ деплоя

### Гипотеза 3: Проблема с `rewrites` для Python функций
- `rewrites` могут не работать для Python serverless функций
- Возможно, нужен другой формат роутинга

---

## Что не удалось проверить

1. **Runtime логи** - не удалось получить логи выполнения из-за ошибок билда
2. **Работоспособность FastAPI на Vercel** - нет подтверждения, что FastAPI вообще работает на Vercel в такой конфигурации
3. **Альтернативные платформы** - не проверяли Railway, Render и другие альтернативы

---

## Рекомендации для следующей сессии

1. **Проверить документацию Vercel** для Python serverless функций с FastAPI
2. **Рассмотреть альтернативные платформы** (Railway, Render) для Python FastAPI приложений
3. **Попробовать другой формат конфигурации** для Vercel (возможно, без `functions` в `vercel.json`)
4. **Проверить примеры** деплоя FastAPI на Vercel в официальной документации или сообществе

---

## Файлы, которые были изменены

- `vercel.json` - убран `runtime`, заменены `routes` на `rewrites`
- `apps/telegram_assistant/requirements.txt` - понижены версии `pydantic` и `httpx`
- `api/index.py` - добавлено логирование
- `apps/telegram_assistant/main.py` - добавлено логирование в endpoint `/health`

---

## Контекст проекта

Проект - монорепо для Telegram бота (AI-ассистент для Bitrix24):
- **Стек:** Python 3.10+, FastAPI, aiogram, Supabase
- **Целевая платформа:** Vercel (serverless functions)
- **Архитектура:** Модульная, монорепо структура
