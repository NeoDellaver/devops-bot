from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from handlers.modules import LESSONS
import json
import os
from dareira_api import dareira_rewrite  # Важно: импорт из корня
from config import ADMIN_USER_ID
# handlers/admin.py

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from dareira_api import dareira_rewrite  # для генерации текста в стиле Рика
import random
import json
import os

# === СПИСОК ТЕМ ДЛЯ СТАТЕЙ ===
ARTICLE_TOPICS = [
    "Кровожадное программирование",
    "Как я убил 3 бага за 5 минут",
    "DevOps и космические корабли",
    "Почему твой Docker контейнер сожрал весь сервер",
    "Секретные приемы от деда Рика для junior DevOps",
    "Как выжить в продакшене без кофе",
    "Почему все боятся iowait",
    "Zombie процессы: как я спас мир от апокалипсиса",
    "Когда стоит использовать top -H и почему это спасет тебе жизнь",
    "Что делать, когда твой сервер плачет от нагрузки",
    "Что такое load average и почему твой сервер не взорвался",
    "Как я обманул OOM Killer и выжил",
    "Секреты systemd, о которых молчат все DevOps'ы",
    "Почему твой swap — это не друг, а враг",
    "Как я научился читать логи быстрее, чем Морти читает мемы"
]

router = Router()

@router.message(Command("restyle"))
async def restyle_all_content(message: Message):
    your_id = message.from_user.id
    await message.answer(f"🔍 Твой ID: {your_id}\n📋 ID админа в конфиге: {ADMIN_USER_ID}")
    
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("🚫 Эта команда только для администратора")
        return
    
    await message.answer("🎨 Начинаю переписывать контент в стиле автора...")
    
    if not os.path.exists("data/author_style.txt"):
        await message.answer("❌ Файл data/author_style.txt не найден")
        return
    
    with open("data/author_style.txt", "r", encoding="utf-8") as f:
        style_prompt = f.read().strip()
    
    if not os.path.exists("data/lessons.json"):
        await message.answer("❌ Файл data/lessons.json не найден")
        return
    
    with open("data/lessons.json", "r", encoding="utf-8") as f:
        lessons = json.load(f)
    
    total_updated = 0
    errors = []
    
    for module, lesson_list in lessons.items():
        for i, lesson in enumerate(lesson_list):
            original = lesson.get("content", "").strip()
            if not original or len(original) < 20:
                continue
            
            try:
                await message.answer(f"✏️ Обрабатываю: {lesson.get('title')}")
                new_content = dareira_rewrite(original, style_prompt)
                
                if not new_content or len(new_content.strip()) < 50:
                    errors.append(f"⚠️ '{lesson.get('title')}' — ответ слишком короткий, оставлен как есть")
                    continue
                
                lesson["content"] = new_content.strip()
                total_updated += 1
                
                import asyncio
                await asyncio.sleep(2)
                
            except Exception as e:
                errors.append(f"⚠️ Ошибка в '{lesson.get('title')}': {str(e)}")
                continue
    
    with open("data/lessons.json", "w", encoding="utf-8") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)
    
    report = f"✨ Готово! Обновлено {total_updated} уроков.\n"
    if errors:
        report += "\n❌ Ошибки:\n" + "\n".join(errors[:5])
    
    await message.answer(report)

