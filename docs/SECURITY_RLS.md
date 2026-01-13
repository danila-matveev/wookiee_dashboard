# Безопасность и RLS (Row Level Security)

## Обзор

Все таблицы в схеме `core` защищены через RLS (Row Level Security) Supabase. Это обеспечивает безопасность на уровне базы данных.

## Принципы RLS

1. **По умолчанию всё запрещено**: RLS включен, политики разрешают доступ
2. **Привязка к пользователю**: Политики используют `auth.uid()` для идентификации пользователя
3. **Роли и права**: Политики проверяют роли через helper функции
4. **Company isolation**: Все данные изолированы по `company_id`

## Связь auth.users → core.employees

**Функция для получения employee_id из user_id:**

```sql
CREATE OR REPLACE FUNCTION core.get_employee_id(user_uuid UUID)
RETURNS UUID AS $$
BEGIN
    RETURN (SELECT id FROM core.employees WHERE user_id = user_uuid);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Функция для получения company_id текущего пользователя:**

```sql
CREATE OR REPLACE FUNCTION core.get_current_company_id()
RETURNS UUID AS $$
BEGIN
    RETURN (
        SELECT company_id 
        FROM core.employees 
        WHERE user_id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Функция для проверки роли:**

```sql
CREATE OR REPLACE FUNCTION core.has_role(employee_uuid UUID, role_slug TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM core.employee_roles er
        JOIN core.roles r ON er.role_id = r.id
        WHERE er.employee_id = employee_uuid
        AND r.slug = role_slug
        AND r.company_id = core.get_current_company_id()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Функция для проверки права:**

```sql
CREATE OR REPLACE FUNCTION core.has_permission(
    employee_uuid UUID, 
    resource_name TEXT, 
    action_name TEXT,
    scope_name TEXT DEFAULT 'own'
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM core.employee_roles er
        JOIN core.role_permissions rp ON er.role_id = rp.role_id
        JOIN core.permissions p ON rp.permission_id = p.id
        WHERE er.employee_id = employee_uuid
        AND p.resource = resource_name
        AND p.action = action_name
        AND p.scope = scope_name
        AND EXISTS (
            SELECT 1 FROM core.roles r 
            WHERE r.id = er.role_id 
            AND r.company_id = core.get_current_company_id()
        )
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## RLS Политики по таблицам

### 1. Companies

**Включение RLS:**
```sql
ALTER TABLE core.companies ENABLE ROW LEVEL SECURITY;
```

**Политика: сотрудники компании могут читать свою компанию**
```sql
CREATE POLICY "Employees can view their company"
ON core.companies
FOR SELECT
USING (
    id = core.get_current_company_id()
);
```

**Политика: только админы могут изменять компанию**
```sql
CREATE POLICY "Admins can update their company"
ON core.companies
FOR UPDATE
USING (
    id = core.get_current_company_id()
    AND core.has_role(core.get_employee_id(auth.uid()), 'admin')
);
```

---

### 2. Employees

**Включение RLS:**
```sql
ALTER TABLE core.employees ENABLE ROW LEVEL SECURITY;
```

**Политика: сотрудники могут читать профили в своей компании**
```sql
CREATE POLICY "Employees can view company employees"
ON core.employees
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);
```

**Политика: сотрудник может изменять свой профиль**
```sql
CREATE POLICY "Employees can update own profile"
ON core.employees
FOR UPDATE
USING (
    user_id = auth.uid()
    AND company_id = core.get_current_company_id()
)
WITH CHECK (
    user_id = auth.uid()
    AND company_id = core.get_current_company_id()
);
```

**Политика: менеджеры могут изменять профили подчинённых**
```sql
CREATE POLICY "Managers can update employee profiles"
ON core.employees
FOR UPDATE
USING (
    company_id = core.get_current_company_id()
    AND (
        core.has_role(core.get_employee_id(auth.uid()), 'admin')
        OR core.has_role(core.get_employee_id(auth.uid()), 'manager')
    )
)
WITH CHECK (
    company_id = core.get_current_company_id()
);
```

---

### 3. Teams

**Включение RLS:**
```sql
ALTER TABLE core.teams ENABLE ROW LEVEL SECURITY;
```

**Политика: сотрудники могут читать команды своей компании**
```sql
CREATE POLICY "Employees can view company teams"
ON core.teams
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);
```

**Политика: менеджеры могут изменять команды**
```sql
CREATE POLICY "Managers can manage teams"
ON core.teams
FOR ALL
USING (
    company_id = core.get_current_company_id()
    AND (
        core.has_role(core.get_employee_id(auth.uid()), 'admin')
        OR core.has_role(core.get_employee_id(auth.uid()), 'manager')
    )
);
```

---

### 4. Roles & Permissions

**Включение RLS:**
```sql
ALTER TABLE core.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.employee_roles ENABLE ROW LEVEL SECURITY;
```

**Политики для Roles:**

```sql
-- Чтение ролей своей компании
CREATE POLICY "Employees can view company roles"
ON core.roles
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);

-- Только админы могут управлять ролями
CREATE POLICY "Admins can manage roles"
ON core.roles
FOR ALL
USING (
    company_id = core.get_current_company_id()
    AND core.has_role(core.get_employee_id(auth.uid()), 'admin')
);
```

**Политики для Permissions:**

```sql
-- Все могут читать права (справочник)
CREATE POLICY "Everyone can view permissions"
ON core.permissions
FOR SELECT
USING (true);
```

**Политики для Employee Roles:**

```sql
-- Чтение назначенных ролей
CREATE POLICY "Employees can view assigned roles"
ON core.employee_roles
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM core.employees e
        WHERE e.id = employee_roles.employee_id
        AND e.company_id = core.get_current_company_id()
    )
);

-- Только админы могут назначать роли
CREATE POLICY "Admins can assign roles"
ON core.employee_roles
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM core.employees e
        WHERE e.id = employee_roles.employee_id
        AND e.company_id = core.get_current_company_id()
    )
    AND core.has_role(core.get_employee_id(auth.uid()), 'admin')
);
```

---

### 5. Products

**Включение RLS:**
```sql
ALTER TABLE core.products ENABLE ROW LEVEL SECURITY;
```

**Политика: сотрудники могут читать продукты своей компании**
```sql
CREATE POLICY "Employees can view company products"
ON core.products
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);
```

**Политика: менеджеры могут управлять продуктами**
```sql
CREATE POLICY "Managers can manage products"
ON core.products
FOR ALL
USING (
    company_id = core.get_current_company_id()
    AND (
        core.has_role(core.get_employee_id(auth.uid()), 'admin')
        OR core.has_role(core.get_employee_id(auth.uid()), 'manager')
    )
);
```

---

### 6. Documents

**Включение RLS:**
```sql
ALTER TABLE core.documents ENABLE ROW LEVEL SECURITY;
```

**Политика: сотрудники могут читать документы своей компании**
```sql
CREATE POLICY "Employees can view company documents"
ON core.documents
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);
```

**Политика: сотрудники могут создавать документы**
```sql
CREATE POLICY "Employees can create documents"
ON core.documents
FOR INSERT
WITH CHECK (
    company_id = core.get_current_company_id()
    AND owner_id = core.get_employee_id(auth.uid())
);
```

**Политика: владелец может изменять/удалять свои документы**
```sql
CREATE POLICY "Owners can manage own documents"
ON core.documents
FOR ALL
USING (
    owner_id = core.get_employee_id(auth.uid())
    AND company_id = core.get_current_company_id()
);
```

---

### 7. Integration Accounts

**Включение RLS:**
```sql
ALTER TABLE core.integration_accounts ENABLE ROW LEVEL SECURITY;
```

**Политика: только админы могут управлять интеграциями**
```sql
CREATE POLICY "Admins can manage integrations"
ON core.integration_accounts
FOR ALL
USING (
    company_id = core.get_current_company_id()
    AND core.has_role(core.get_employee_id(auth.uid()), 'admin')
);
```

---

### 8. Tasks

**Включение RLS:**
```sql
ALTER TABLE core.tasks ENABLE ROW LEVEL SECURITY;
```

**Политика: сотрудники могут читать задачи своей компании**
```sql
CREATE POLICY "Employees can view company tasks"
ON core.tasks
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);
```

**Политика: сотрудники могут создавать задачи**
```sql
CREATE POLICY "Employees can create tasks"
ON core.tasks
FOR INSERT
WITH CHECK (
    company_id = core.get_current_company_id()
    AND creator_id = core.get_employee_id(auth.uid())
);
```

**Политика: назначенный сотрудник и создатель могут изменять задачу**
```sql
CREATE POLICY "Assigned and creators can update tasks"
ON core.tasks
FOR UPDATE
USING (
    company_id = core.get_current_company_id()
    AND (
        assignee_id = core.get_employee_id(auth.uid())
        OR creator_id = core.get_employee_id(auth.uid())
        OR core.has_role(core.get_employee_id(auth.uid()), 'manager')
    )
);
```

---

### 9. Calendar Events

**Включение RLS:**
```sql
ALTER TABLE core.calendar_events ENABLE ROW LEVEL SECURITY;
```

**Политика: сотрудники могут читать события своей компании**
```sql
CREATE POLICY "Employees can view company events"
ON core.calendar_events
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);
```

**Политика: сотрудники могут создавать события**
```sql
CREATE POLICY "Employees can create events"
ON core.calendar_events
FOR INSERT
WITH CHECK (
    company_id = core.get_current_company_id()
    AND organizer_id = core.get_employee_id(auth.uid())
);
```

**Политика: организатор может изменять событие**
```sql
CREATE POLICY "Organizers can update events"
ON core.calendar_events
FOR UPDATE
USING (
    company_id = core.get_current_company_id()
    AND (
        organizer_id = core.get_employee_id(auth.uid())
        OR core.has_role(core.get_employee_id(auth.uid()), 'manager')
    )
);
```

---

### 10. Agents

**Включение RLS:**
```sql
ALTER TABLE core.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE core.agent_logs ENABLE ROW LEVEL SECURITY;
```

**Политики для Agents:**

```sql
-- Чтение агентов своей компании
CREATE POLICY "Employees can view company agents"
ON core.agents
FOR SELECT
USING (
    company_id = core.get_current_company_id()
);

-- Только админы могут управлять агентами
CREATE POLICY "Admins can manage agents"
ON core.agents
FOR ALL
USING (
    company_id = core.get_current_company_id()
    AND core.has_role(core.get_employee_id(auth.uid()), 'admin')
);
```

**Политики для Agent Runs:**

```sql
-- Чтение запусков агентов своей компании
CREATE POLICY "Employees can view company agent runs"
ON core.agent_runs
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM core.agents a
        WHERE a.id = agent_runs.agent_id
        AND a.company_id = core.get_current_company_id()
    )
);
```

---

## Supabase Storage (RLS для файлов)

**Бакеты:**
- `company-documents` - документы компаний
- `company-avatars` - аватары сотрудников

**Политика для company-documents:**

```sql
-- Чтение: сотрудники своей компании
CREATE POLICY "Employees can view company documents"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'company-documents'
    AND (
        (storage.foldername(name))[1] = core.get_current_company_id()::TEXT
    )
);

-- Запись: сотрудники своей компании
CREATE POLICY "Employees can upload company documents"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'company-documents'
    AND (
        (storage.foldername(name))[1] = core.get_current_company_id()::TEXT
    )
);

-- Удаление: владелец или админ
CREATE POLICY "Owners can delete documents"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'company-documents'
    AND (
        (storage.foldername(name))[1] = core.get_current_company_id()::TEXT
        AND core.has_role(core.get_employee_id(auth.uid()), 'admin')
    )
);
```

---

## Аудит и логирование

**Таблица аудита (опционально):**

```sql
CREATE TABLE core.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES core.companies(id) ON DELETE CASCADE,
    
    employee_id UUID NOT NULL REFERENCES core.employees(id) ON DELETE CASCADE,
    action TEXT NOT NULL,  -- create, update, delete, read
    resource_type TEXT NOT NULL,  -- employees, tasks, etc.
    resource_id UUID,
    
    changes JSONB,  -- до/после изменений
    ip_address TEXT,
    user_agent TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_company_id ON core.audit_logs(company_id);
CREATE INDEX idx_audit_logs_employee_id ON core.audit_logs(employee_id);
CREATE INDEX idx_audit_logs_created_at ON core.audit_logs(created_at);
```

**RLS для audit_logs:**

```sql
ALTER TABLE core.audit_logs ENABLE ROW LEVEL SECURITY;

-- Только админы могут читать логи аудита
CREATE POLICY "Admins can view audit logs"
ON core.audit_logs
FOR SELECT
USING (
    company_id = core.get_current_company_id()
    AND core.has_role(core.get_employee_id(auth.uid()), 'admin')
);
```

---

## Best Practices

1. **Всегда проверяйте company_id**: Политики должны изолировать данные по компании
2. **Используйте helper функции**: `core.get_current_company_id()`, `core.has_role()` и т.д.
3. **Минимальные права**: Давайте только необходимые права (SELECT, INSERT, UPDATE, DELETE по отдельности)
4. **Тестируйте политики**: Создавайте тесты для проверки RLS политик
5. **Документируйте**: Описывайте права доступа в документации модулей

---

## Тестирование RLS

**Пример теста (для разработки):**

```sql
-- Тест: пользователь не может читать данные другой компании
SET ROLE authenticated;
SET request.jwt.claim.sub = 'user-from-company-a-uuid'::text;

-- Должно вернуть 0 строк
SELECT * FROM core.employees WHERE company_id != core.get_current_company_id();
```

---

## Следующие шаги

1. Изучить `docs/DOMAIN_MODEL.md` - доменная модель
2. Изучить `docs/REPO_STRUCTURE.md` - как организован код
3. Приступить к миграциям (Этап 1 плана миграции)
