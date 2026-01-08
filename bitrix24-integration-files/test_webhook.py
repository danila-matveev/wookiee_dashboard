"""
Простой скрипт для проверки работоспособности вебхука Bitrix24
Используйте этот скрипт перед запуском основной выгрузки данных
"""
import requests
from config import BITRIX24_DOMAIN, BITRIX24_WEBHOOK, USE_WEBHOOK

def test_webhook():
    """
    Проверяет работоспособность вебхука Bitrix24
    """
    print("=" * 60)
    print("🔍 Проверка вебхука Bitrix24")
    print("=" * 60)
    
    # Проверка настроек
    if not BITRIX24_DOMAIN:
        print("\n❌ ОШИБКА: Не указан BITRIX24_DOMAIN в config.py")
        return False
    
    if not BITRIX24_WEBHOOK:
        print("\n❌ ОШИБКА: Не указан BITRIX24_WEBHOOK в config.py")
        return False
    
    if not USE_WEBHOOK:
        print("\n⚠️  ВНИМАНИЕ: В config.py указано USE_WEBHOOK = False")
        print("   Этот скрипт предназначен для проверки вебхука.")
        print("   Для проверки токена используйте test_connection.py")
        return False
    
    print(f"\n📋 Настройки:")
    print(f"   Домен: {BITRIX24_DOMAIN}")
    print(f"   Вебхук URL: {BITRIX24_WEBHOOK[:50]}...")
    
    # Формируем URL для запроса
    webhook_url = BITRIX24_WEBHOOK.rstrip('/')
    api_url = f"{webhook_url}/user.get"
    
    print(f"\n📡 Отправляю тестовый запрос...")
    print(f"   URL: {api_url}")
    
    try:
        # Простой запрос для проверки подключения
        params = {
            'start': 0,
            'filter': {
                'ACTIVE': True
            }
        }
        
        response = requests.post(api_url, json=params, timeout=10)
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        # Проверяем ответ
        try:
            data = response.json()
        except ValueError:
            print(f"\n❌ ОШИБКА: Сервер вернул не JSON ответ")
            print(f"   Ответ: {response.text[:200]}")
            return False
        
        # Проверяем на ошибки API
        if 'error' in data:
            error_code = data.get('error', 'неизвестно')
            error_desc = data.get('error_description', 'нет описания')
            
            print(f"\n❌ ОШИБКА API:")
            print(f"   Код: {error_code}")
            print(f"   Описание: {error_desc}")
            
            # Даем советы по исправлению
            print(f"\n💡 Рекомендации:")
            
            if error_code == 'NO_AUTH_FOUND':
                print("   1. Проверьте, что вебхук URL скопирован полностью")
                print("   2. Убедитесь, что в конце URL есть '/'")
                print("   3. Проверьте, что вебхук не был удален в Bitrix24")
                print("   4. Создайте новый вебхук и обновите URL в config.py")
            
            elif error_code == 'insufficient_scope':
                print("   1. Откройте настройки вебхука в Bitrix24")
                print("   2. Добавьте права доступа: 'user' и 'user_basic'")
                print("   3. Сохраните изменения")
            
            elif error_code == 'invalid_token' or response.status_code == 401:
                print("   1. Вебхук истек или был удален")
                print("   2. Создайте новый вебхук в Bitrix24")
                print("   3. Обновите URL в config.py")
            
            elif error_code == 'QUERY_LIMIT_EXCEEDED':
                print("   1. Слишком много запросов за короткое время")
                print("   2. Подождите несколько минут и попробуйте снова")
            
            else:
                print("   1. Проверьте правильность вебхук URL")
                print("   2. Убедитесь, что вебхук активен в Bitrix24")
                print("   3. Проверьте интернет-соединение")
            
            return False
        
        # Если все хорошо
        if 'result' in data:
            users = data.get('result', [])
            total = data.get('total', 0)
            
            print(f"\n✅ Вебхук работает отлично!")
            print(f"\n📊 Результаты теста:")
            print(f"   Получено пользователей: {len(users)}")
            print(f"   Всего в системе: {total}")
            
            if users:
                print(f"\n👤 Пример первого пользователя:")
                first_user = users[0]
                print(f"   ID: {first_user.get('ID')}")
                print(f"   Имя: {first_user.get('NAME', 'не указано')}")
                print(f"   Фамилия: {first_user.get('LAST_NAME', 'не указано')}")
                print(f"   Email: {first_user.get('EMAIL', 'не указано')}")
                print(f"   Должность: {first_user.get('WORK_POSITION', 'не указана')}")
            
            print(f"\n✅ Тест пройден успешно!")
            print(f"   Теперь вы можете запустить: python3 bitrix24_export.py")
            return True
        
        else:
            print(f"\n⚠️  Неожиданный формат ответа:")
            print(data)
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n❌ ОШИБКА: Превышено время ожидания ответа")
        print(f"   Проверьте интернет-соединение")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ОШИБКА: Не удалось подключиться к серверу")
        print(f"   Проверьте:")
        print(f"   1. Интернет-соединение")
        print(f"   2. Правильность домена: {BITRIX24_DOMAIN}")
        print(f"   3. Что Bitrix24 доступен по адресу https://{BITRIX24_DOMAIN}")
        return False
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    print("\n")
    success = test_webhook()
    print("\n" + "=" * 60)
    if success:
        print("✅ Готово к работе!")
    else:
        print("❌ Требуется исправление настроек")
    print("=" * 60 + "\n")

