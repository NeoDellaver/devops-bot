# handlers/progress.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import json
from database import get_user
from utils.xp_system import get_status_by_xp
from .modules import get_modules_keyboard

router = Router()

@router.callback_query(F.data == "progress")
async def show_progress(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден.", show_alert=True)
        return

    xp = user[2]
    status = get_status_by_xp(xp)
    completed = len(json.loads(user[5])) if user[5] != "[]" else 0

    # Подсчёт общего числа уроков
    with open("data/lessons.json", encoding="utf-8") as f:
        all_lessons = json.load(f)
    total = sum(len(lessons) for lessons in all_lessons.values())

    # Формируем текст без Markdown
    text = (
        f"📊 Твой прогресс\n\n"
        f"• Статус: {status}\n"
        f"• Опыт (XP): {xp}\n"
        f"• Пройдено: {completed}/{total} уроков"
    )

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_modules_keyboard()
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Игнорируем, если содержимое не изменилось
            pass
        else:
            # Для других ошибок — показываем уведомление
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
    
    await callback.answer()  # Убираем "часики" с кнопки