import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_user, update_user_progress, is_user_premium
from config import ADMIN_USER_ID

router = Router()

# Загрузка уроков
with open("data/lessons.json", encoding="utf-8") as f:
    LESSONS = json.load(f)

# Единственный бесплатный модуль
FREE_MODULES = {"linux"}

# === КЛАВИАТУРЫ ===

def get_modules_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐧 Linux", callback_data="module:linux")],
        [InlineKeyboardButton(text="🌐 Сети", callback_data="module:networking")],
        [InlineKeyboardButton(text="🗄️ Базы данных", callback_data="module:databases")],
        [InlineKeyboardButton(text="⚙️ Ansible", callback_data="module:ansible")],
        [InlineKeyboardButton(text="🐳 Docker", callback_data="module:docker")],
        [InlineKeyboardButton(text="🚀 CI/CD", callback_data="module:cicd")],
        [InlineKeyboardButton(text="☸️ Kubernetes", callback_data="module:kubernetes")],
        [InlineKeyboardButton(text="🔍 Мониторинг", callback_data="module:monitoring")],
        [InlineKeyboardButton(text="📊 Прогресс", callback_data="progress")],
        [InlineKeyboardButton(text="🧠 Dareira AI", callback_data="dareira_help")]
    ])

def get_lessons_keyboard(module: str, available_lessons: list, completed: set, lessons: list):
    buttons = []
    for i in available_lessons:
        status = " ✅" if (module, str(i)) in completed else ""
        title = f"{i+1}. {lessons[i]['title']}{status}"
        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"lesson:{module}:{i}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_modules")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_test_keyboard(options: list, module: str, lesson_idx: int):
    kb = []
    for i, opt in enumerate(options):
        kb.append([
            InlineKeyboardButton(
                text=opt,
                callback_data=f"answer:{module}:{lesson_idx}:{i}"
            )
        ])
    kb.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_test")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_premium_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Оформить премиум-доступ", callback_data="premium_offer")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_modules")]
    ])

# === FSM ===

class TestState(StatesGroup):
    in_test = State()

# === ОБРАБОТЧИКИ ===

@router.callback_query(F.data == "back_to_modules")
async def back_to_modules(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Выбери модуль:",
        reply_markup=get_modules_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("module:"))
async def show_lessons_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    module = callback.data.split(":")[1]
    
    # Проверка доступа
    user_id = callback.from_user.id
    if user_id != ADMIN_USER_ID and module not in FREE_MODULES:
        if not await is_user_premium(user_id):
            await callback.message.edit_text(
                "🔒 Этот модуль доступен только по премиум-подписке.\n\n"
                "Получи доступ ко всем DevOps-материалам: Сети, Docker, Kubernetes, CI/CD и другим!",
                parse_mode="HTML",
                reply_markup=get_premium_keyboard()
            )
            return

    lessons = LESSONS.get(module, [])
    if not lessons:
        await callback.message.edit_text("Модуль пока пуст.")
        return

    user = await get_user(user_id)
    completed = set()
    if user and user[5] != "[]":
        try:
            completed = {tuple(item.split(":")) for item in json.loads(user[5])}
        except:
            pass

    # Логика доступа к урокам
    if user_id == ADMIN_USER_ID:
        available_lessons = list(range(len(lessons)))
    else:
        if not completed:
            next_lesson = 0
        else:
            max_lesson = max((int(idx) for mod, idx in completed if mod == module), default=-1)
            next_lesson = max_lesson + 1
        available_lessons = []
        for i in range(len(lessons)):
            if (module, str(i)) in completed or i == next_lesson:
                available_lessons.append(i)
            if i > next_lesson:
                break

    keyboard = get_lessons_keyboard(module, available_lessons, completed, lessons)
    await callback.message.edit_text(
        f"📚 Модуль: {module.capitalize()}",
        reply_markup=keyboard
    )

# --- Остальные обработчики (без изменений) ---

@router.callback_query(F.data.startswith("lesson:"))
async def show_lesson_full(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    _, module, lesson_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    lesson = LESSONS[module][lesson_idx]

    await callback.message.delete()

    await callback.message.answer(
        f"📖 <b>Урок {lesson_idx+1}: {lesson['title']}</b>\n\n{lesson['content']}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Пройти тест", callback_data=f"start_test:{module}:{lesson_idx}")],
            [InlineKeyboardButton(text="🔙 Назад к урокам", callback_data=f"module:{module}")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("start_test:"))
async def start_test(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    questions = LESSONS[module][lesson_idx]["questions"]

    await state.set_state(TestState.in_test)
    await state.update_data(
        module=module,
        lesson_idx=lesson_idx,
        questions=questions,
        current_idx=0,
        correct=0
    )

    await callback.message.delete()
    await send_question(callback.message, state)
    await callback.answer()

async def send_question(message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    idx = data["current_idx"]

    if idx >= len(questions):
        correct = data["correct"]
        total = len(questions)
        module = data["module"]
        lesson_idx = data["lesson_idx"]

        if correct == total:
            xp = 10
        elif total > 0 and correct >= total * 0.6:
            xp = 5
        else:
            xp = 0

        if xp > 0:
            user = await get_user(message.chat.id)
            if user:
                completed = json.loads(user[5]) if user[5] != "[]" else []
                key = f"{module}:{lesson_idx}"
                if key not in completed:
                    completed.append(key)
                    await update_user_progress(
                        message.chat.id, module, lesson_idx, xp, json.dumps(completed)
                    )

        await message.answer(
            f"🎉 Тест завершён!\nПравильно: {correct}/{total}\n+{xp} XP",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📚 Вернуться к урокам", callback_data=f"module:{module}")]
            ])
        )
        await state.clear()
        return

    q = questions[idx]
    await message.answer(
        f"❓ Вопрос {idx+1}/{len(questions)}\n\n{q['text']}",
        reply_markup=get_test_keyboard(q["options"], data["module"], data["lesson_idx"])
    )

@router.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx, answer_idx = callback.data.split(":")
    answer_idx = int(answer_idx)

    data = await state.get_data()
    if "questions" not in data:
        await state.clear()
        await callback.message.answer("❌ Тест был прерван. Начните заново.")
        return

    idx = data["current_idx"]
    q = data["questions"][idx]
    correct = data["correct"]

    if answer_idx == q["correct"]:
        correct += 1
        await callback.message.answer("✅ Верно!")
    else:
        await callback.message.answer(f"❌ Неверно.\nПравильный ответ: {q['options'][q['correct']]}")

    await state.update_data(current_idx=idx + 1, correct=correct)
    await callback.message.delete()
    await send_question(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "cancel_test")
async def cancel_test(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "↩️ Возврат в главное меню",
        reply_markup=get_modules_keyboard()
    )
    await callback.answer()