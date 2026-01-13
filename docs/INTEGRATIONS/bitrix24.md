# Интеграция Bitrix24

## Обзор

Интеграция с Bitrix24 через REST API для синхронизации сотрудников, задач, событий календаря.

## Архитектура

```
┌─────────────────────────────────────────────────┐
│         Wookiee Dashboard Platform              │
│  ┌──────────────────────────────────────────┐   │
│  │    Integration SDK (Bitrix24)            │   │
│  │  ┌────────────┐  ┌────────────┐         │   │
│  │  │  Client    │  │   Sync     │         │   │
│  │  └─────┬──────┘  └──────┬─────┘         │   │
│  └────────┼─────────────────┼───────────────┘   │
└───────────┼─────────────────┼───────────────────┘
            │                 │
            │                 ▼
            │         ┌───────────────┐
            │         │  Core SDK     │
            │         │  (Supabase)   │
            │         └───────────────┘
            │
            ▼
┌─────────────────────────────────────────────────┐
│              Bitrix24 REST API                  │
│  https://your-domain.bitrix24.ru/rest/...       │
└─────────────────────────────────────────────────┘
```

## Аутентификация

### Webhook (рекомендуемый)

**Способ**: Incoming Webhook (не требует OAuth)

**Настройка**:
1. В Bitrix24: **Приложения → Входящий вебхук**
2. Создать вебхук с правами:
   - `user` - пользователи
   - `task` - задачи (опционально)
   - `calendar` - календарь (опционально)
   - `im` - сообщения (для подтверждения кода)
3. Сохранить URL вебхука

**Хранение в Core**:
```sql
INSERT INTO core.integration_accounts (company_id, provider, name, credentials, status)
VALUES (
    'company-id',
    'bitrix24',
    'Основной Bitrix24',
    '{"webhook_url": "https://your-domain.bitrix24.ru/rest/1/xxx/"}'::jsonb,
    'active'
);
```

### OAuth 2.0 (опционально)

Для публичных приложений или если нужны дополнительные права.

## Компоненты

### Bitrix24 Client

**Расположение**: `packages/integrations/src/integrations/bitrix24/client.py`

**Назначение**: HTTP клиент для работы с Bitrix24 REST API.

**Основные методы**:
- `get_users(filters)` - получить сотрудников
- `get_user_by_email(email)` - найти пользователя по email
- `create_task(fields)` - создать задачу
- `get_tasks(filters)` - получить задачи
- `create_event(fields)` - создать событие календаря
- `get_events(filters)` - получить события

**Пример использования**:

```python
from integrations.bitrix24 import Bitrix24Client

client = Bitrix24Client(
    webhook_url="https://your-domain.bitrix24.ru/rest/1/xxx/"
)

# Получить сотрудников
users = client.get_users(filter={"ACTIVE": True})

# Создать задачу
task = client.create_task({
    "TITLE": "Купить молоко",
    "RESPONSIBLE_ID": "123",
    "DEADLINE": "2025-01-15"
})
```

### Синхронизация данных

**Расположение**: `packages/integrations/src/integrations/bitrix24/sync.py`

**Назначение**: Синхронизация данных между Bitrix24 и Core.

**Процесс синхронизации**:
1. Получить данные из Bitrix24 (через Client)
2. Преобразовать в формат Core (маппинг полей)
3. Сохранить в Core через Core SDK

**Пример маппинга сотрудников**:

```python
def map_bitrix_user_to_employee(bitrix_user: dict, company_id: UUID) -> dict:
    return {
        "company_id": company_id,
        "email": bitrix_user.get("EMAIL"),
        "full_name": f"{bitrix_user.get('NAME')} {bitrix_user.get('LAST_NAME')}".strip(),
        "first_name": bitrix_user.get("NAME"),
        "last_name": bitrix_user.get("LAST_NAME"),
        "position": bitrix_user.get("WORK_POSITION"),
        "phone": bitrix_user.get("PERSONAL_MOBILE") or bitrix_user.get("WORK_PHONE"),
        "metadata": {
            "bitrix_id": bitrix_user.get("ID"),
            "bitrix_departments": bitrix_user.get("UF_DEPARTMENT", []),
            "bitrix_active": bitrix_user.get("ACTIVE")
        }
    }
```

## Хранение данных

### Integration Accounts

**Таблица**: `core.integration_accounts`

**Назначение**: Хранение учётных данных и настроек интеграций.

**Пример**:
```sql
SELECT * FROM core.integration_accounts
WHERE provider = 'bitrix24' AND company_id = '...';
```

### Синхронизация сотрудников

**Процесс**:
1. Получить всех активных сотрудников из Bitrix24
2. Для каждого сотрудника:
   - Найти в `core.employees` по `metadata->>'bitrix_id'`
   - Если не найден - создать нового
   - Если найден - обновить данные
3. Записать в `core.integration_sync_logs`

**Утилита миграции**: `scripts/export-bitrix24.py` (однократная выгрузка)

## Webhook'и (опционально)

### Входящие webhook'и от Bitrix24

Для реального времени можно настроить webhook'и от Bitrix24.

**События**:
- `ONUSERADD` - новый сотрудник
- `ONTASKADD` - новая задача
- `ONCALENDAREVENTADD` - новое событие

**Обработка**:
- Создать endpoint (FastAPI/Next.js API Route)
- Получить webhook от Bitrix24
- Синхронизировать данные

## Ограничения API

**Rate Limiting**:
- Bitrix24 ограничивает количество запросов
- Рекомендуется: retry с экспоненциальной задержкой

**Обработка ошибок**:
- `QUERY_LIMIT_EXCEEDED` - retry
- `NO_AUTH_FOUND` - ошибка конфигурации
- `insufficient_scope` - недостаточно прав

**Пример обработки**:

```python
def call_bitrix_api(method: str, params: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = requests.post(f"{webhook_url}/{method}", json=params)
            data = response.json()
            
            if "error" in data:
                if data["error"] == "QUERY_LIMIT_EXCEEDED":
                    time.sleep(2 ** attempt)  # экспоненциальная задержка
                    continue
                else:
                    raise BitrixAPIError(data["error"])
            
            return data["result"]
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

## Миграция существующего кода

**Текущее расположение**: `bitrix24-integration-files/bitrix24_export.py`

**Целевое расположение**: 
- `packages/integrations/src/integrations/bitrix24/client.py`
- `packages/integrations/src/integrations/bitrix24/sync.py`

**Изменения**:
- Вместо SQLite → Core SDK (Supabase)
- Вместо `config.py` → `core.integration_accounts`
- Добавить логирование в `core.integration_sync_logs`

**План миграции** (см. `docs/MIGRATION_PLAN.md`, Этап 2):
1. Создать Integration SDK
2. Перенести код из `bitrix24_export.py`
3. Адаптировать под Core SDK
4. Протестировать синхронизацию
5. Архивировать старые файлы

## Документация Bitrix24

**Официальная документация**:
- [REST API](https://apidocs.bitrix24.com/)
- [Список методов](https://apidocs.bitrix24.com/api-reference/index.html)
- [Доступ к REST API](https://apidocs.bitrix24.com/first-steps/access-to-rest-api.html)

**Важные методы**:
- `user.get` - получить сотрудников
- `tasks.task.add` - создать задачу
- `tasks.task.list` - получить задачи
- `calendar.event.add` - создать событие
- `calendar.event.get` - получить события
- `im.notify` - отправить уведомление (для подтверждения кода)

## Следующие шаги

1. Изучить `docs/PLATFORM_OVERVIEW.md` - обзор платформы
2. Изучить `docs/DOMAIN_MODEL.md` - доменная модель (раздел Integration Accounts)
3. Создать Integration SDK (Этап 2 плана миграции)
4. Настроить синхронизацию сотрудников
