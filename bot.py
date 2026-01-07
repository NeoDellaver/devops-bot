import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from database import init_db
from config import BOT_TOKEN
from handlers import start, modules, dareira, progress, admin

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

dp = Dispatcher()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

async def main():
    logger.info("🔧 Инициализация базы данных...")
    await init_db()
    
    logger.info("🤖 Удаление webhook'ов и запуск polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(modules.router)
    dp.include_router(dareira.router)
    dp.include_router(progress.router)
    dp.include_router(admin.router)
    
    logger.info("🚀 Запуск polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
