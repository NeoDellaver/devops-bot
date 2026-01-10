#!/bin/bash
# 🔧 Скрипт восстановления devops-bot

set -e

echo "🔧 ВОССТАНОВЛЕНИЕ DEVOPS-BOT..."
echo ""

cd /root/devops-bot

# Шаг 1: Остановить сервис
echo "🛑 Остановка сервиса..."
sudo systemctl stop devops-bot.service

sleep 2

# Шаг 2: Очистить старые логи
echo "🗑️  Очистка логов..."
sudo rm -f logs/bot.log*
mkdir -p logs

# Шаг 3: Стащить свежую версию с GitHub
echo "📥 Получение свежей версии..."
git reset --hard
git pull origin master

# Шаг 4: Пересоздать venv
echo "🔄 Пересоздание виртуального окружения..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Шаг 5: Обновить pip и установить зависимости
echo "📦 Установка зависимостей..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Шаг 6: Проверить синтаксис
echo "✔️ Проверка синтаксиса..."
# Сначала исправить кодировку
python3 fix_encoding.py

# Потом проверить синтаксис
python3 -m py_compile bot.py config.py database.py || {
    echo "❌ Ошибка синтаксиса!"
    exit 1
}

# Шаг 7: Проверить конфиг
echo "🔐 Проверка конфига..."
if grep -q "BOT_TOKEN\|API_KEY" .env 2>/dev/null; then
    echo "✅ .env файл существует"
else
    echo "⚠️ Убедитесь, что .env файл настроен!"
fi

# Шаг 8: Запустить сервис
echo "🚀 Запуск сервиса..."
sudo systemctl start devops-bot.service

# Шаг 9: Проверить статус
sleep 3
echo ""
echo "📋 Статус сервиса:"
sudo systemctl status devops-bot.service --no-pager | head -10

# Шаг 10: Показать логи
echo ""
echo "📊 Последние логи:"
sudo journalctl -u devops-bot.service -n 30 --no-pager

echo ""
echo "✅ Восстановление завершено!"
