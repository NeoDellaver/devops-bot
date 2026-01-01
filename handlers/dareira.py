from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dareira_api import ask_dareira
from .modules import get_modules_keyboard
import html

router = Router()

class DareiraState(StatesGroup):
    waiting_for_question = State()

@router.callback_query(F.data == "dareira_help")
async def dareira_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напиши свой вопрос по DevOps (например: «Как работает Docker?»):")
    await state.set_state(DareiraState.waiting_for_question)

@router.message(DareiraState.waiting_for_question)
async def dareira_answer(message: Message, state: FSMContext):
    thinking_msg = await message.answer("🤔 Dareira думает...")
    answer = await ask_dareira(message.text)
    await thinking_msg.delete()  # Удаляем "думает", чтобы не засорять чат
    await message.answer(
        f"<b>🧠 Dareira отвечает:</b>\n\n{html.escape(answer)}",
        parse_mode="HTML",
        reply_markup=get_modules_keyboard()
    )
    await state.clear()