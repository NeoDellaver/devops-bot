# handlers/start.py
from aiogram import Router, F
from aiogram.types import Message
from database import get_user, create_user
from utils.xp_system import get_status_by_xp
from .modules import get_modules_keyboard

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await create_user(message.from_user.id, message.from_user.username)
        user = (message.from_user.id, message.from_user.username, 0, "linux", 0, "[]")
    
    xp = user[2]
    status = get_status_by_xp(xp)
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        f"Ты — {status} (XP: {xp})\n\n"
        "Готов учиться DevOps? Выбери модуль:",
        reply_markup=get_modules_keyboard()
    )