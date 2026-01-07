from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import json
import logging
from database import get_user
from utils.xp_system import get_status_by_xp
from .modules import get_modules_keyboard

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "progress")
async def show_progress(callback: CallbackQuery):
    try:
        user = await get_user(callback.from_user.id)
        if not user:
            await callback.answer("⚠️ Профиль не найден. Отправьте /start.", show_alert=True)
            return

        xp = user[2] if len(user) > 2 else 0
        status = get_status_by_xp(xp)
        try:
            completed = len(json.loads(user[5])) if user[5] not in (None, "[]", "") else 0
        except (json.JSONDecodeError, TypeError):
            completed = 0

        # Кэшируйте lessons.json в продакшене! Сейчас — для простоты:
        with open("data/lessons.json", encoding="utf-8") as f:
            all_lessons = json.load(f)
        total = sum(len(lessons) for lessons in all_lessons.values())

        text = (
            f"📊 Твой прогресс\n\n"
            f"• Статус: {status}\n"
            f"• Опыт (XP): {xp}\n"
            f"• Пройдено: {completed}/{total} уроков"
        )

        await callback.message.edit_text(
            text=text,
            reply_markup=get_modules_keyboard()
        )

    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Игнорируем: содержимое не изменилось
            pass
        elif "message to edit not found" in str(e):
            # Сообщение удалено → отправляем новое
            await callback.message.answer(
                "📊 Твой прогресс (обновлён):\n\n"
                f"• Статус: {status}\n"
                f"• Опыт (XP): {xp}\n"
                f"• Пройдено: {completed}/{total} уроков",
                reply_markup=get_modules_keyboard()
            )
        else:
            logger.exception("TelegramBadRequest в show_progress")
            await callback.answer(f"⚠️ Ошибка: {str(e)}", show_alert=True)

    except Exception as e:
        logger.exception("Критическая ошибка в show_progress")
        await callback.answer("⚠️ Не удалось загрузить прогресс. Попробуйте позже.", show_alert=True)

    finally:
        await callback.answer()  # Убираем "часики"
