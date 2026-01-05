# handlers/restyle.py
import os
import json
import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from dareira_api import ask_dareira

router = Router()

PROMPT_PATH = "data/rewrite_prompt.txt"
LESSONS_PATH = "data/lessons.json"

def load_prompt() -> str:
    if not os.path.isfile(PROMPT_PATH):
        raise FileNotFoundError(f"Файл промпта не найден: {PROMPT_PATH}")
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

async def rewrite_text_with_prompt(text: str, prompt_template: str) -> str:
    prompt = prompt_template.replace("{content}", text)
    result = await ask_dareira(prompt)
    return result[:4000].strip()

@router.message(Command("restyle"))
async def handle_restyle(message: types.Message):
    try:
        # 1. Загружаем промпт
        prompt_template = load_prompt()
        await message.answer("🔄 Промпт загружен. Начинаю переписывание уроков...")

        # 2. Загружаем уроки
        if not os.path.isfile(LESSONS_PATH):
            await message.answer("❌ Файл lessons.json не найден")
            return

        with open(LESSONS_PATH, "r", encoding="utf-8") as f:
            lessons = json.load(f)

        total_updated = 0

        # 3. Обходим ВСЕ модули (monitoring, docker и т.д.)
        for module_name, lessons_list in lessons.items():
            if not isinstance(lessons_list, list):
                continue  # пропускаем не-списки

            for i, lesson in enumerate(lessons_list):
                if not isinstance(lesson, dict) or "content" not in lesson:
                    continue

                original = lesson["content"]
                if not original or not original.strip():
                    continue

                try:
                    await message.answer(f"♻️ Обрабатываю: {lesson.get('title', f'{module_name}[{i}]')}")

                    rewritten = await rewrite_text_with_prompt(original, prompt_template)
                    lesson["content"] = rewritten
                    total_updated += 1

                    # Сохраняем после каждого урока — защита от падения
                    with open(LESSONS_PATH, "w", encoding="utf-8") as f:
                        json.dump(lessons, f, ensure_ascii=False, indent=2)

                    await asyncio.sleep(1)  # уважаем лимиты Yandex API

                except Exception as e:
                    await message.answer(f"⚠️ Ошибка в {module_name}[{i}]: {str(e)[:100]}")

        await message.answer(f"✅ Готово! Переписано {total_updated} уроков. Все сообщения теперь читаемы в Telegram!")

    except FileNotFoundError as e:
        await message.answer(f"❌ Ошибка: {e}")
    except Exception as e:
        await message.answer(f"💥 Критическая ошибка: {str(e)}")
