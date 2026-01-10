## 🚨 БОТ НЕ ЗАПУСКАЕТСЯ? ВЫПОЛНИТЕ ЭТИ КОМАНДЫ

### Быстрое восстановление (скопируйте и вставьте всё):

```bash
cd /root/devops-bot && \
chmod +x recover.sh diagnose.sh && \
./recover.sh
```

---

### Или пошагово:

**1️⃣ Сначала диагностика - посмотрите ошибку:**
```bash
cd /root/devops-bot
chmod +x diagnose.sh
./diagnose.sh
```

**2️⃣ Затем восстановление:**
```bash
cd /root/devops-bot
chmod +x recover.sh
./recover.sh
```

**3️⃣ Если всё ещё не работает - логи:**
```bash
sudo journalctl -u devops-bot.service -n 100 -f
```

---

### 🔍 Возможные проблемы:

**❌ Ошибка: "pip: command not found"**
```bash
# Решение: используйте python3 -m pip
python3 -m pip install -r requirements.txt
```

**❌ Ошибка: "No module named 'aiogram'"**
```bash
# Решение: активируйте venv
source venv/bin/activate
pip install -r requirements.txt
```

**❌ Ошибка: "BOT_TOKEN not found"**
```bash
# Убедитесь, что .env файл существует и содержит:
cat .env | grep BOT_TOKEN
```

**❌ Git конфликт с data/lessons.json**
```bash
# Решение: заберите версию с GitHub
git checkout -- data/lessons.json
git pull origin master
```

---

### 🆘 ПОСЛЕДНЯЯ ОПЦИЯ - ПОЛНАЯ ПЕРЕУСТАНОВКА:

```bash
cd /root/devops-bot

# Остановить сервис
sudo systemctl stop devops-bot.service

# Удалить всё лишнее
git reset --hard
git pull origin master
rm -rf venv logs/bot.log*
mkdir -p logs

# Пересоздать окружение
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Запустить
sudo systemctl start devops-bot.service

# Проверить
sudo systemctl status devops-bot.service
sudo journalctl -u devops-bot.service -n 50
```

---

## 📞 ЕСЛИ НУЖНА ПОМОЩЬ

Соберите информацию:
```bash
echo "=== GIT ===" && git status && git log --oneline -3
echo -e "\n=== PYTHON ===" && python3 --version && which python3
echo -e "\n=== DEPENDENCIES ===" && pip list | grep aiogram
echo -e "\n=== LOGS ===" && sudo journalctl -u devops-bot.service -n 50 --no-pager
```

И поделитесь этим выводом!
