#!/bin/bash

# Скрипт для настройки Telegram webhook после деплоя на Vercel
# Использование: ./scripts/setup_telegram_webhook.sh

set -e

echo "🔧 Настройка Telegram Webhook для Wookiee AI Assistant"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Запрашиваем данные
read -p "Введите токен Telegram бота (TELEGRAM_BOT_TOKEN): " BOT_TOKEN
read -p "Введите URL вашего Vercel проекта (например, https://wookiee-dashboard.vercel.app): " VERCEL_URL

# Убираем слеш в конце, если есть
VERCEL_URL="${VERCEL_URL%/}"
WEBHOOK_URL="${VERCEL_URL}/webhook/telegram"

echo ""
echo "📋 Проверка данных:"
echo "   Bot Token: ${BOT_TOKEN:0:10}..."
echo "   Webhook URL: ${WEBHOOK_URL}"
echo ""

# Шаг 1: Проверка /health endpoint
echo "1️⃣  Проверка /health endpoint..."
HEALTH_URL="${VERCEL_URL}/health"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "${HEALTH_URL}" || echo -e "\n000")

HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Health check успешен: ${BODY}${NC}"
else
    echo -e "${RED}❌ Health check не прошёл (HTTP ${HTTP_CODE})${NC}"
    echo "   Проверьте, что проект задеплоен на Vercel"
    exit 1
fi

echo ""

# Шаг 2: Проверка текущего webhook
echo "2️⃣  Проверка текущего webhook..."
WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
echo "   Текущий webhook:"
echo "$WEBHOOK_INFO" | python3 -m json.tool 2>/dev/null || echo "$WEBHOOK_INFO"
echo ""

# Шаг 3: Установка webhook
echo "3️⃣  Установка webhook..."
SET_WEBHOOK_RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
    -d "url=${WEBHOOK_URL}")

if echo "$SET_WEBHOOK_RESPONSE" | grep -q '"ok":true'; then
    echo -e "${GREEN}✅ Webhook успешно установлен!${NC}"
else
    echo -e "${RED}❌ Ошибка при установке webhook:${NC}"
    echo "$SET_WEBHOOK_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SET_WEBHOOK_RESPONSE"
    exit 1
fi

echo ""

# Шаг 4: Проверка установленного webhook
echo "4️⃣  Проверка установленного webhook..."
FINAL_WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo")
echo "$FINAL_WEBHOOK_INFO" | python3 -m json.tool 2>/dev/null || echo "$FINAL_WEBHOOK_INFO"

echo ""
echo -e "${GREEN}🎉 Настройка завершена!${NC}"
echo ""
echo "📝 Следующие шаги:"
echo "   1. Откройте Telegram и найдите вашего бота"
echo "   2. Отправьте команду: /start your@email.com"
echo "   3. Проверьте логи в Vercel Dashboard → Deployments → Functions → View Function Logs"
echo ""
