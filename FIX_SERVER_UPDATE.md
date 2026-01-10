# 🔧 Инструкция по обновлению бота на сервере

## Проблема
При попытке обновления возникают ошибки:
```
error: Your local changes to the following files would be overwritten by merge:
        data/lessons.json
-bash: pip: command not found
```

## Решение

### Шаг 1: Разрешить конфликт с data/lessons.json

```bash
cd /root/devops-bot

# Опция A: Сохранить локальные изменения (рекомендуется)
git stash

# Или Опция B: Отбросить локальные изменения
# git checkout -- data/lessons.json
```

### Шаг 2: Получить обновления

```bash
git pull origin master
```

### Шаг 3: Установить зависимости

```bash
# Используйте правильный путь к pip (через venv или python3)
cd /root/devops-bot

# Способ 1: Через venv (если он создан)
source venv/bin/activate
pip install -r requirements.txt

# Способ 2: Если venv не существует, создайте его
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Способ 3: Прямой вызов python3 -m pip
python3 -m pip install -r requirements.txt
```

### Шаг 4: Перезагрузить сервис

```bash
sudo systemctl restart devops-bot.service

# Проверить статус
sudo systemctl status devops-bot.service

# Посмотреть логи
sudo journalctl -u devops-bot.service -n 50 -f
```

## 📋 Полная команда (скопировать и вставить)

```bash
cd /root/devops-bot && \
git stash && \
git pull origin master && \
source venv/bin/activate && \
pip install -r requirements.txt && \
sudo systemctl restart devops-bot.service && \
echo "✅ Обновление завершено!" && \
sudo systemctl status devops-bot.service
```

## ✅ Что было изменено в коде

### 1. requirements.txt
- Убраны дубликаты aiogram
- Убран встроенный модуль sqlite3
- Закреплены версии: aiogram==3.13.0, aiohttp==3.9.1, python-dotenv==1.0.0

### 2. bot.py
- Восстановлена полная обработка ошибок (middleware, error_handler)
- TelegramNetworkError теперь обрабатывается корректно
- Добавлены таймауты (30 сек)

### 3. handlers/modules.py
- Все обработчики обёрнуты в try/except
- Безопасное удаление сообщений
- Отправка сообщений через bot.send_message()

### 4. dareira_api.py
- Добавлены таймауты для HTTP запросов (15-30 сек)

### 5. handlers/dareira.py, start.py
- Добавлена обработка ошибок
- Улучшена работа с асинхронными функциями

## 🐛 Что это исправляет

✅ **TelegramNetworkError: ServerDisconnect** — больше не блокирует работу
✅ **Кнопки не реагируют на старте** — лучше обработка таймаутов
✅ **Ошибка back_to_modules** — добавлена fallback логика
✅ **Конфликты парсинга** — оптимизирована работа с API

## 📞 Если что-то не работает

Проверьте логи:
```bash
sudo journalctl -u devops-bot.service -n 100 | grep -E "ERROR|Traceback|Exception"
```

Проверьте процесс:
```bash
ps aux | grep bot.py
```

Перезагрузите вручную:
```bash
sudo systemctl stop devops-bot.service
sleep 2
sudo systemctl start devops-bot.service
```
