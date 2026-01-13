# Обзор AI-агентов Wookiee Dashboard Platform

## Обзор

AI-агенты платформы используют единый AI Gateway для работы с различными LLM провайдерами (OpenRouter, OpenAI, Anthropic, локальные модели).

## Архитектура

```
┌─────────────────────────────────────────────────┐
│              Apps/Modules                        │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ Telegram Bot │  │ Web Dashboard│             │
│  └──────┬───────┘  └──────┬───────┘             │
└─────────┼──────────────────┼─────────────────────┘
          │                  │
┌─────────┴──────────────────┴─────────────────────┐
│           AI Gateway SDK                          │
│  ┌──────────────────────────────────────────┐    │
│  │  AI Gateway Client                       │    │
│  │  ┌────────┐  ┌────────┐  ┌────────┐     │    │
│  │  │OpenRout│  │OpenAI  │  │Local   │     │    │
│  │  │Adapter │  │Adapter │  │Adapter │     │    │
│  │  └────────┘  └────────┘  └────────┘     │    │
│  └──────────────────────────────────────────┘    │
└───────────────────────────────────────────────────┘
          │                  │
┌─────────┴──────────────────┴─────────────────────┐
│       LLM Providers                               │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐│
│  │ OpenRouter │  │  OpenAI    │  │   Ollama    ││
│  └────────────┘  └────────────┘  └─────────────┘│
└───────────────────────────────────────────────────┘
```

## AI Gateway SDK

**Расположение**: `packages/ai-gateway/`

**Назначение**: Единый интерфейс для работы с различными LLM провайдерами.

**Основные компоненты**:
- `client.py` - основной клиент
- `adapters/` - адаптеры для разных провайдеров
  - `openrouter.py` - OpenRouter (рекомендуемый)
  - `openai.py` - OpenAI
  - `anthropic.py` - Anthropic Claude
  - `local.py` - Ollama (локальные модели)

**Пример использования**:

```python
from ai_gateway import AIGatewayClient

# Инициализация
client = AIGatewayClient(
    provider="openrouter",  # или "openai", "anthropic", "local"
    api_key="sk-or-v1-xxx",
    model="openai/gpt-4"  # или "anthropic/claude-3-opus", "mistral/mistral-medium"
)

# Простой запрос
response = client.complete(
    prompt="Создай задачу: купить молоко",
    temperature=0.7,
    max_tokens=500
)

# Tool calling (для агентов)
response = client.complete_with_tools(
    prompt="Создай задачу",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Создать задачу",
                "parameters": {...}
            }
        }
    ]
)
```

## Хранение данных агентов

**Таблицы в Core**:
- `core.agents` - конфигурация агентов
- `core.agent_tools` - инструменты агентов
- `core.agent_runs` - запуски агентов
- `core.agent_logs` - логи агентов

**Схема** (см. `docs/DOMAIN_MODEL.md`):
- `agents.config` - промпты, модели, параметры
- `agent_runs.input_data` / `output_data` - входные/выходные данные
- `agent_logs` - детальные логи выполнения

## Типы агентов

### 1. Task Assistant (Помощник задач)

**Назначение**: Создание и управление задачами через естественный язык.

**Инструменты**:
- `create_task(title, description, due_date, assignee_id)` - создать задачу
- `get_tasks(filters)` - получить задачи
- `update_task(task_id, fields)` - обновить задачу
- `complete_task(task_id)` - завершить задачу

**Пример использования** (Telegram):
```
Пользователь: "Создай задачу купить молоко на завтра"
Бот: "✅ Задача создана: Купить молоко (дедлайн: завтра)"
```

### 2. Calendar Assistant (Помощник календаря)

**Назначение**: Создание и управление событиями календаря.

**Инструменты**:
- `create_event(title, start_at, end_at, participants)` - создать событие
- `get_events(date)` - получить события
- `update_event(event_id, fields)` - обновить событие
- `cancel_event(event_id)` - отменить событие

**Пример использования** (Telegram):
```
Пользователь: "Встреча с командой завтра в 15:00 на 1 час"
Бот: "✅ Событие создано: Встреча с командой (завтра 15:00-16:00)"
```

### 3. Custom Agents (Пользовательские агенты)

**Назначение**: Агенты для специфичных задач (FinManager, Blogger CRM и т.д.).

**Принципы**:
- Агенты регистрируются в `core.agents`
- Инструменты определяются в `core.agent_tools`
- Каждый модуль может создать своих агентов

## Наблюдаемость

**Логирование**:
- Все запуски агентов записываются в `core.agent_runs`
- Детальные логи - в `core.agent_logs`
- Уровни: INFO, WARNING, ERROR

**Мониторинг**:
- Количество запусков
- Время выполнения
- Ошибки
- Использование токенов (через AI Gateway)

**Пример запроса логов**:

```sql
-- Последние запуски агента
SELECT * FROM core.agent_runs
WHERE agent_id = '...'
ORDER BY started_at DESC
LIMIT 10;

-- Логи ошибок
SELECT * FROM core.agent_logs
WHERE agent_run_id IN (
    SELECT id FROM core.agent_runs WHERE status = 'failed'
)
AND level = 'ERROR';
```

## Безопасность

**RLS политики**:
- Сотрудники могут читать агентов своей компании
- Только админы могут управлять агентами
- Логи доступны только админам

**Ограничения**:
- Rate limiting (через AI Gateway)
- Валидация входных данных
- Санитизация промптов

## Интеграция с модулями

**Как модуль добавляет агента**:

1. Создать миграцию:
```sql
INSERT INTO core.agents (company_id, name, description, agent_type, config)
VALUES (
    'company-id',
    'FinManager Assistant',
    'Помощник для финансового менеджера',
    'custom',
    '{
        "model": "openai/gpt-4",
        "prompt": "Ты помощник финансового менеджера...",
        "temperature": 0.7
    }'::jsonb
);
```

2. Зарегистрировать инструменты:
```sql
INSERT INTO core.agent_tools (agent_id, name, tool_type, config)
VALUES (
    'agent-id',
    'create_transaction',
    'function_call',
    '{
        "function": {
            "name": "create_transaction",
            "description": "...",
            "parameters": {...}
        }
    }'::jsonb
);
```

3. Использовать в модуле:
```python
from ai_gateway import AIGatewayClient
from core_sdk import get_agent

agent = get_agent("finmanager_assistant")
client = AIGatewayClient(provider="openrouter", api_key="...")

response = client.complete_with_tools(
    prompt=user_message,
    tools=agent.tools
)
```

## Следующие шаги

1. Изучить `docs/PLATFORM_OVERVIEW.md` - обзор платформы
2. Изучить `docs/DOMAIN_MODEL.md` - доменная модель (раздел Agents)
3. Создать AI Gateway SDK (Этап 3 плана миграции)
4. Создать первых агентов (Task Assistant, Calendar Assistant)
