# handlers/payment.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice
from database import is_user_premium, set_user_premium
from config import STAR_PRICE
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "buy_course")
async def process_buy_course(callback: CallbackQuery):
    if await is_user_premium(callback.from_user.id):
        await callback.answer("✅ У вас уже есть доступ!", show_alert=True)
        return

    # Отправка инвойса в Telegram Stars
    await callback.message.answer_invoice(
        title="📚 Полный курс DevOps",
        description="Все уроки, тесты и обновления навсегда",
        payload="devops_full_access",
        currency="XTR",  # ← Telegram Stars
        prices=[LabeledPrice(label="Курс", amount=STAR_PRICE)],
        start_parameter="devops_course",
        need_name=False,
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False,
        is_flexible=False
    )
    await callback.answer()

@router.message(F.content_type == "successful_payment")
async def process_successful_payment(message: Message):
    logger.info(f"Stars оплата от {message.from_user.id}")
    await set_user_premium(message.from_user.id, True)
    
    await message.answer(
        "🎉 Спасибо за покупку!\n\n"
        "Теперь у вас **полный доступ** ко всем урокам курса DevOps!\n"
        "Нажмите /start и вперёд к вершине! 🚀"
    )
