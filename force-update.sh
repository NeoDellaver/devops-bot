#!/bin/bash
# 🔄 Принудительное обновление с удалением кэша

cd /root/devops-bot

echo "🛑 Остановка сервиса..."
sudo systemctl stop devops-bot.service

sleep 2

echo "🔄 Принудительное получение обновлений..."
# Удалить локальные изменения и получить свежую версию
git reset --hard HEAD
git clean -fd
git fetch --all
git reset --hard origin/master

echo "📊 Проверка bot.py на строке 113:"
sed -n '108,120p' bot.py

echo ""
echo "🚀 Запуск сервиса..."
sudo systemctl start devops-bot.service

sleep 3

echo "📋 Статус:"
sudo systemctl status devops-bot.service --no-pager | head -10

echo ""
echo "📊 Логи (последние 30 строк):"
sudo journalctl -u devops-bot.service -n 30 --no-pager
