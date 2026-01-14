# Предложение решения проблемы с деплоем на Vercel

**Дата:** 2026-01-13  
**Проблема:** Vercel не распознаёт `api/index.py` как serverless функцию

---

## Анализ проблемы

### Текущая ошибка
```
Error: The pattern "api/index.py" defined in functions doesn't match any Serverless Functions inside the api directory.
```

### Причина
Vercel автоматически обнаруживает Python файлы в папке `api/` как serverless функции, но использование секции `functions` в `vercel.json` может конфликтовать с автоматическим обнаружением.

---

## Решение #1: Убрать секцию `functions` из `vercel.json` (рекомендуется)

Vercel автоматически обнаруживает Python файлы в папке `api/` без явной конфигурации в `functions`.

**Новая конфигурация `vercel.json`:**
```json
{
  "rewrites": [
    { "source": "/health", "destination": "/api/index.py" },
    { "source": "/webhook/telegram", "destination": "/api/index.py" },
    { "source": "/jobs/morning_digest", "destination": "/api/index.py" },
    { "source": "/jobs/evening_digest", "destination": "/api/index.py" }
  ]
}
```

**Преимущества:**
- Проще конфигурация
- Соответствует стандартному подходу Vercel для Python
- Vercel автоматически определит `api/index.py` как serverless функцию

---

## Решение #2: Использовать другой формат для Python функций

Если решение #1 не сработает, можно попробовать использовать явное указание через `builds` (старый формат, но может работать):

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    { "src": "/health", "dest": "/api/index.py" },
    { "src": "/webhook/telegram", "dest": "/api/index.py" },
    { "src": "/jobs/morning_digest", "dest": "/api/index.py" },
    { "src": "/jobs/evening_digest", "dest": "/api/index.py" }
  ]
}
```

**Примечание:** Формат `builds` устарел, но может работать для Python функций.

---

## Решение #3: Альтернативная структура (если Vercel не подходит)

Если Vercel продолжает вызывать проблемы, рассмотреть альтернативные платформы:

### 3.1. Railway
- ✅ Хорошая поддержка Python/FastAPI
- ✅ Простой деплой
- ✅ Бесплатный tier
- ❌ Может быть медленнее Vercel

### 3.2. Render
- ✅ Хорошая поддержка Python/FastAPI
- ✅ Простой деплой
- ✅ Бесплатный tier (с ограничениями)
- ❌ Может быть медленнее Vercel

### 3.3. Fly.io
- ✅ Хорошая поддержка Python/FastAPI
- ✅ Глобальная сеть
- ✅ Бесплатный tier
- ❌ Более сложная настройка

---

## Рекомендуемый план действий

1. **Попробовать Решение #1** (убрать `functions` из `vercel.json`)
2. Если не работает → **Попробовать Решение #2** (формат `builds`)
3. Если всё ещё не работает → **Рассмотреть Решение #3** (альтернативные платформы)

---

## Дополнительные проверки

1. Убедиться, что `requirements.txt` находится в корне проекта
2. Убедиться, что все зависимости совместимы (уже исправлено)
3. Проверить, что переменные окружения установлены в Vercel Dashboard
4. Проверить документацию Vercel для Python serverless functions
