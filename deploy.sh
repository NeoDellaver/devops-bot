#!/bin/bash
cd /root/devops-bot
git pull origin master
systemctl restart devops-bot
echo "✅ Сервер обновлен и перезагружен"
