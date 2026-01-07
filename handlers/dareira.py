from aiogram import Router, F
from aiogram.types import Message
from dareira_api import ask_dareira
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text.startswith("/dareira"))
async def dareira_command(message: Message):
    try:
        question = message.text[9:].strip()
        if not question:
            await message.answer(
                "🧠 **Dareira AI**\n\n"
                "Задай любой вопрос по DevOps!\n"
                "Примеры:\n"
                "`/dareira Что такое Load Average?`\n"
                "`/dareira Как работает Docker?`\n"
                "`/dareira Почему мой K8s под в статусе CrashLoopBackOff?`",
                parse_mode="Markdown"
            )
            return

        thinking_msg = await message.answer("⏳ Думаю...")

        # ⚠️ КРИТИЧЕСКИ ВАЖНО: если `ask_dareira` — синхронная функция,
        # она БЛОКИРУЕТ event loop! Нужно запускать в executor.
        import asyncio
        loop = asyncio.get_running_loop()
        answer = await loop.run_in_executor(None, ask_dareira, question)

        # Удаляем "Думаю..." перед отправкой ответа (опционально)
        try:
            await thinking_msg.delete()
        except Exception:
            pass  # Игнорируем, если не удалось удалить

        # Экранируем Markdown-спецсимволы в ответе, если используем parse_mode
        # Но проще — отправить без форматирования
        await message.answer(answer)

    except Exception as e:
        logger.exception("Ошибка в /dareira")
        try:
            await message.answer("💥 Не удалось получить ответ от Dareira AI. Попробуйте позже.")
        except Exception:
            pass
