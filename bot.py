import asyncio
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.exceptions import TelegramAPIError, TelegramNetworkError
from database import init_db
from config import BOT_TOKEN
from handlers import start, modules, dareira, progress, admin

# === Настройка логирования ===
class UserContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user'):
            record.user = 'Unknown'
        if not hasattr(record, 'user_id'):
            record.user_id = 'Unknown'
        return True

def setup_logging():
    os.makedirs("logs", exist_ok=True)

    log_format = (
        "%(asctime)s - %(levelname)s - "
        "[User: %(user)s | ID: %(user_id)s] - %(message)s"
    )
    datefmt = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(fmt=log_format, datefmt=datefmt)

    # Файловый логгер с ротацией
    file_handler = RotatingFileHandler(
        "logs/bot.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(UserContextFilter())

    # Консольный логгер
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(UserContextFilter())

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True
    )

# === Middleware для логирования входящих событий ===
async def log_middleware(handler, event, data):
    logger = logging.getLogger(__name__)
    extra = {"user": "Unknown", "user_id": "Unknown"}

    if isinstance(event, Message):
        user = event.from_user
        extra["user"] = f"{user.full_name} (@{user.username})" if user.username else user.full_name
        extra["user_id"] = user.id
        text = event.text or event.caption or f"<{event.content_type}>"
        logger.info(f"📩 Получено сообщение: '{text}'", extra=extra)

    elif isinstance(event, CallbackQuery):
        user = event.from_user
        extra["user"] = f"{user.full_name} (@{user.username})" if user.username else user.full_name
        extra["user_id"] = user.id
        logger.info(f"🔘 Нажата кнопка: data='{event.data}'", extra=extra)

    return await handler(event, data)

# === Обработчик ошибок (aiogram 3.x) с retry логикой ===
async def error_handler(event: ErrorEvent, **kwargs):
    logger = logging.getLogger(__name__)
    extra = {"user": "Unknown", "user_id": "Unknown"}

    exception = event.exception
    update = event.update

    if update and update.message:
        user = update.message.from_user
        extra["user"] = f"{user.full_name} (@{user.username})" if user.username else user.full_name
        extra["user_id"] = user.id
    elif update and update.callback_query:
        user = update.callback_query.from_user
        extra["user"] = f"{user.full_name} (@{user.username})" if user.username else user.full_name
        extra["user_id"] = user.id

    if isinstance(exception, TelegramNetworkError):
        logger.warning(f"⚠️ Сетевая ошибка (временная): {exception}", extra=extra)
        # Не логируем как критическую ошибку - это временный сбой
    elif isinstance(exception, TelegramAPIError):
        logger.error(f"❌ Telegram API Error: {exception}", extra=extra)
    else:
        logger.exception("💥 Необработанное исключение:", exc_info=exception, extra=extra)

    return True  # подавляем дальнейшее распространение ошибки

# === Основная функция ===
async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🔧 Инициализация базы данных...")
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN,
            request_timeout=30  # 30 секунд таймаут для запросов
        )
    )
    dp = Dispatcher()

    # Подключаем middleware и обработчик ошибок
    dp.update.middleware(log_middleware)
    dp.errors.register(error_handler)

    # Роутеры
    dp.include_router(start.router)
    dp.include_router(modules.router)
    dp.include_router(dareira.router)
    dp.include_router(progress.router)
    dp.include_router(admin.router)

    logger.info("🤖 Удаление webhook'ов и запуск polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"⚠️ Не удалось удалить webhook: {e}")

    logger.info("🚀 Запуск polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
