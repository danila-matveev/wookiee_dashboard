"""
Скрипт для выгрузки сотрудников из Bitrix24 и сохранения в базу данных
"""
import requests
import sqlite3
import json
from config import BITRIX24_DOMAIN, BITRIX24_WEBHOOK, USE_WEBHOOK
import os

# Проверка наличия настроек
if not BITRIX24_DOMAIN or not BITRIX24_WEBHOOK:
    print("❌ ОШИБКА: Сначала заполните файл config.py!")
    print("   Укажите BITRIX24_DOMAIN и BITRIX24_WEBHOOK")
    exit(1)

# Формируем URL для API запроса
if USE_WEBHOOK:
    # Если используем вебхук, URL уже содержит все необходимое
    api_url = BITRIX24_WEBHOOK.rstrip('/') + '/user.get'
    headers = None
else:
    # Если используем Bearer токен (OAuth/MCP токен)
    api_url = f"https://{BITRIX24_DOMAIN}/rest/user.get"
    # Убираем "Bearer " из начала токена, если он там есть
    token = BITRIX24_WEBHOOK.replace('Bearer ', '').strip()
    headers = {'Content-Type': 'application/json'}

def get_all_users():
    """
    Получает всех сотрудников из Bitrix24
    """
    print("📡 Подключаюсь к Bitrix24...")
    
    all_users = []
    start = 0
    
    while True:
        # Параметры запроса
        params = {
            'start': start,
            'filter': {
                'ACTIVE': True,  # Только активные пользователи
                'USER_TYPE': 'employee'  # Только сотрудники (не внешние пользователи)
            }
        }
        
        try:
            if USE_WEBHOOK:
                response = requests.post(api_url, json=params)
            else:
                # Для OAuth/MCP токена передаем токен в параметре 'auth'
                params_with_auth = params.copy()
                token = BITRIX24_WEBHOOK.replace('Bearer ', '').strip()
                params_with_auth['auth'] = token
                response = requests.post(api_url, json=params_with_auth, headers=headers)
            
            response.raise_for_status()
            data = response.json()
            
            # Проверяем на ошибки
            if 'error' in data:
                print(f"❌ Ошибка API: {data['error']}")
                if 'error_description' in data:
                    print(f"   Описание: {data['error_description']}")
                return None
            
            # Получаем список пользователей
            users = data.get('result', [])
            
            if not users:
                break
            
            all_users.extend(users)
            print(f"   Получено сотрудников: {len(all_users)}")
            
            # Проверяем, есть ли еще данные
            total = data.get('total', 0)
            if len(all_users) >= total:
                break
            
            start += len(users)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе к Bitrix24: {e}")
            return None
    
    print(f"✅ Всего получено сотрудников: {len(all_users)}")
    return all_users

def create_database():
    """
    Создает базу данных SQLite для хранения сотрудников
    """
    db_path = 'employees.db'
    
    # Подключаемся к базе данных (создастся автоматически, если не существует)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу сотрудников
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bitrix_id TEXT UNIQUE NOT NULL,
            name TEXT,
            last_name TEXT,
            second_name TEXT,
            full_name TEXT,
            email TEXT,
            position TEXT,
            department_ids TEXT,
            phone TEXT,
            active INTEGER,
            date_register TEXT,
            last_login TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print(f"✅ База данных создана: {db_path}")
    return conn

def save_users_to_db(conn, users):
    """
    Сохраняет сотрудников в базу данных
    """
    cursor = conn.cursor()
    
    saved_count = 0
    updated_count = 0
    
    for user in users:
        # Формируем полное имя
        name_parts = []
        if user.get('NAME'):
            name_parts.append(user['NAME'])
        if user.get('SECOND_NAME'):
            name_parts.append(user['SECOND_NAME'])
        if user.get('LAST_NAME'):
            name_parts.append(user['LAST_NAME'])
        full_name = ' '.join(name_parts) if name_parts else user.get('NAME', '')
        
        # Обрабатываем отделы (может быть массивом)
        department_ids = user.get('UF_DEPARTMENT', [])
        if isinstance(department_ids, list):
            department_ids_str = ','.join(map(str, department_ids))
        else:
            department_ids_str = str(department_ids) if department_ids else ''
        
        # Проверяем, существует ли уже такой сотрудник
        cursor.execute('SELECT id FROM employees WHERE bitrix_id = ?', (user['ID'],))
        exists = cursor.fetchone()
        
        if exists:
            # Обновляем существующую запись
            cursor.execute('''
                UPDATE employees SET
                    name = ?,
                    last_name = ?,
                    second_name = ?,
                    full_name = ?,
                    email = ?,
                    position = ?,
                    department_ids = ?,
                    phone = ?,
                    active = ?,
                    date_register = ?,
                    last_login = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE bitrix_id = ?
            ''', (
                user.get('NAME', ''),
                user.get('LAST_NAME', ''),
                user.get('SECOND_NAME', ''),
                full_name,
                user.get('EMAIL', ''),
                user.get('WORK_POSITION', ''),
                department_ids_str,
                user.get('PERSONAL_MOBILE', '') or user.get('WORK_PHONE', ''),
                1 if user.get('ACTIVE', False) else 0,
                user.get('DATE_REGISTER', ''),
                user.get('LAST_LOGIN', ''),
                user['ID']
            ))
            updated_count += 1
        else:
            # Добавляем нового сотрудника
            cursor.execute('''
                INSERT INTO employees (
                    bitrix_id, name, last_name, second_name, full_name,
                    email, position, department_ids, phone, active,
                    date_register, last_login
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user['ID'],
                user.get('NAME', ''),
                user.get('LAST_NAME', ''),
                user.get('SECOND_NAME', ''),
                full_name,
                user.get('EMAIL', ''),
                user.get('WORK_POSITION', ''),
                department_ids_str,
                user.get('PERSONAL_MOBILE', '') or user.get('WORK_PHONE', ''),
                1 if user.get('ACTIVE', False) else 0,
                user.get('DATE_REGISTER', ''),
                user.get('LAST_LOGIN', '')
            ))
            saved_count += 1
    
    conn.commit()
    print(f"✅ Сохранено новых: {saved_count}, обновлено: {updated_count}")
    return saved_count + updated_count

def export_to_json(users, filename='employees.json'):
    """
    Экспортирует данные в JSON файл для резервной копии
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print(f"✅ Резервная копия сохранена: {filename}")

def main():
    """
    Главная функция - выполняет весь процесс выгрузки
    """
    print("=" * 50)
    print("🚀 Начало выгрузки сотрудников из Bitrix24")
    print("=" * 50)
    
    # Шаг 1: Получаем всех сотрудников
    users = get_all_users()
    
    if not users:
        print("❌ Не удалось получить данные сотрудников")
        return
    
    # Шаг 2: Создаем базу данных
    conn = create_database()
    
    # Шаг 3: Сохраняем в базу данных
    print("\n💾 Сохраняю данные в базу данных...")
    save_users_to_db(conn, users)
    
    # Шаг 4: Создаем резервную копию в JSON
    print("\n📄 Создаю резервную копию в JSON...")
    export_to_json(users)
    
    # Закрываем соединение с базой данных
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Выгрузка завершена успешно!")
    print("=" * 50)
    print(f"\n📊 Результаты:")
    print(f"   - Всего сотрудников: {len(users)}")
    print(f"   - База данных: employees.db")
    print(f"   - Резервная копия: employees.json")

if __name__ == '__main__':
    main()

