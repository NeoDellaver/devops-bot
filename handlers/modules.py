import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_user, update_user_progress
from dareira_api import dareira_rewrite  # Важно: импорт из корня
from config import ADMIN_USER_ID

router = Router()

# Загрузка уроков
with open("data/lessons.json", encoding="utf-8") as f:
    LESSONS = json.load(f)

# === КЛАВИАТУРЫ ===

def get_modules_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Посмотреть статистику", callback_data="show_image")],
        [InlineKeyboardButton(text="📖 Прочитать статью", callback_data="show_article")],
        [InlineKeyboardButton(text="🐧 Linux", callback_data="module:linux")],
        [InlineKeyboardButton(text="🌐 Сети", callback_data="module:networking")],
        [InlineKeyboardButton(text="🗄️ Базы данных", callback_data="module:databases")],
        [InlineKeyboardButton(text="⚙️ Ansible", callback_data="module:ansible")],
        [InlineKeyboardButton(text="🐳 Docker", callback_data="module:docker")],
        [InlineKeyboardButton(text="🚀 CI/CD", callback_data="module:cicd")],
        [InlineKeyboardButton(text="☸️ Kubernetes", callback_data="module:kubernetes")],
        [InlineKeyboardButton(text="🔍 Мониторинг", callback_data="module:monitoring")],
        [InlineKeyboardButton(text="🧠 Dareira AI", callback_data="dareira_help")]
    ])

def get_lessons_keyboard(module: str, available_lessons: list, completed: set, lessons: list):
    buttons = []
    for i in available_lessons:
        status = " ✅" if (module, str(i)) in completed else ""
        title = f"{i + 1}. {lessons[i]['title']}{status}"
        buttons.append([
            InlineKeyboardButton(text=title, callback_data=f"lesson:{module}:{i}")
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_modules")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_test_keyboard(options: list, module: str, lesson_idx: int):
    kb = []
    for i, opt in enumerate(options):
        kb.append([
            InlineKeyboardButton(text=opt, callback_data=f"answer:{module}:{lesson_idx}:{i}")
        ])
    kb.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_test")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# === ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ДЛИННЫХ СООБЩЕНИЙ ===

async def send_long_message(message, text: str, parse_mode="Markdown", reply_markup=None, **kwargs):
    """
    Отправляет длинное сообщение, разбивая его на части ≤ 4000 символов.
    Клавиатура (reply_markup) прикрепляется только к первому сообщению.
    """
    MAX_LEN = 4000
    parts = []
    current = text

    while len(current) > MAX_LEN:
        split_pos = current.rfind("\n", 0, MAX_LEN)
        if split_pos == -1:
            split_pos = current.rfind(" ", 0, MAX_LEN)
        if split_pos == -1:
            split_pos = MAX_LEN

        parts.append(current[:split_pos])
        current = current[split_pos:].lstrip()

    if current:
        parts.append(current)

    for i, part in enumerate(parts):
        if i == 0:
            await message.answer(part, parse_mode=parse_mode, reply_markup=reply_markup, **kwargs)
        else:
            await message.answer(part, parse_mode=parse_mode, **kwargs)

# === FSM ===

class TestState(StatesGroup):
    in_test = State()

# === ОБРАБОТЧИКИ ===

@router.callback_query(F.data == "back_to_modules")
async def back_to_modules(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Выбери модуль:", reply_markup=get_modules_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("module:"))
async def show_lessons_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    module = callback.data.split(":", 1)[1]

    lessons = LESSONS.get(module)
    if not lessons:
        await callback.message.edit_text("Модуль пока пуст.")
        return

    user = await get_user(callback.from_user.id)
    completed = set()
    if user and user[5] not in (None, "[]", ""):
        try:
            completed_str_list = json.loads(user[5])
            completed = {(mod, str(idx)) for (mod, idx) in [tuple(item.split(":", 1)) for item in completed_str_list]}
        except (json.JSONDecodeError, ValueError, TypeError):
            pass

    # ВСЕ УРОКИ ДОСТУПНЫ ВСЕМ
    available_lessons = list(range(len(lessons)))

    keyboard = get_lessons_keyboard(module, available_lessons, completed, lessons)
    await callback.message.edit_text(
        f"📚 Модуль: {module.capitalize()}",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("lesson:"))
async def show_lesson_full(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    _, module, lesson_idx = callback.data.split(":", 2)
    lesson_idx = int(lesson_idx)
    lesson = LESSONS[module][lesson_idx]

    await callback.message.delete()

    full_text = f"📖 **Урок {lesson_idx + 1}: {lesson['title']}**\n\n{lesson['content']}"

    # Отправляем с разбивкой, клавиатура — только к первому сообщению
    await send_long_message(
        callback.message,
        full_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Пройти тест", callback_data=f"start_test:{module}:{lesson_idx}")],
            [InlineKeyboardButton(text="🔙 Назад к урокам", callback_data=f"module:{module}")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("start_test:"))
async def start_test(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":", 2)
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
    current_idx = data["current_idx"]
    total = len(questions)

    if current_idx >= total:
        correct = data["correct"]
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
                try:
                    completed = json.loads(user[5]) if user[5] not in (None, "[]", "") else []
                except (json.JSONDecodeError, TypeError):
                    completed = []
                key = f"{module}:{lesson_idx}"
                if key not in completed:
                    completed.append(key)
                    await update_user_progress(
                        message.chat.id, module, lesson_idx, xp, json.dumps(completed)
                    )

        # ДОБАВЛЕНА КНОПКА «ПОДЕЛИТЬСЯ»
        share_text = f"Я набрал {correct} из {total} по DevOps! Проверь себя →"
        share_url = f"https://t.me/share/url?url=https://t.me/devvvops_bot&text={share_text.replace(' ', '%20')}"

        await message.answer(
            f"🎉 Тест завершён!\nПравильно: {correct}/{total}\n+{xp} XP",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📤 Поделиться результатом", url=share_url)],
                [InlineKeyboardButton(text="📚 Вернуться к урокам", callback_data=f"module:{module}")]
            ])
        )
        await state.clear()
        return

    q = questions[current_idx]
    await message.answer(
        f"❓ Вопрос {current_idx + 1}/{total}\n\n{q['text']}",
        reply_markup=get_test_keyboard(q["options"], data["module"], data["lesson_idx"])
    )

@router.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    _, module, lesson_idx, answer_idx = parts
    answer_idx = int(answer_idx)

    data = await state.get_data()
    if "questions" not in data:
        await state.clear()
        await callback.message.answer("❌ Тест был прерван. Начните заново.")
        return

    current_idx = data["current_idx"]
    questions = data["questions"]
    if current_idx >= len(questions):
        await callback.answer("Тест уже завершён.", show_alert=True)
        return

    q = questions[current_idx]
    correct = data["correct"]

    if answer_idx == q["correct"]:
        correct += 1
        await callback.message.answer("✅ Верно!")
    else:
        await callback.message.answer(f"❌ Неверно.\nПравильный ответ: {q['options'][q['correct']]}")

    await state.update_data(current_idx=current_idx + 1, correct=correct)
    await callback.message.delete()
    await send_question(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "cancel_test")
async def cancel_test(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("↩️ Возврат в главное меню", reply_markup=get_modules_keyboard())
    await callback.answer()

# === НОВЫЕ ОБРАБОТЧИКИ: КАРТИНКИ И СТАТЬИ ===

@router.callback_query(F.data == "show_image")
async def show_image(callback: CallbackQuery):
    img_url = "https://i.imgur.com/5KQbZ7l.png"
    caption = "🧠 **Статистика обучения DevOps**\n\n" \
              "→ 85% джунов боятся терминала\n" \
              "→ 92% не знают разницы между Load Average и CPU%\n" \
              "→ 76% не проходят собеседования из-за пробелов в знаниях\n\n" \
              "🔥 Dareira закрывает эти пробелы за 5 минут в день."
    
    await callback.message.answer_photo(
        photo=img_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Вернуться к урокам", callback_data="back_to_modules")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "show_article")
async def show_article(callback: CallbackQuery):
    article_text = (
        "🚀 **Почему DevOps — это не про инструменты, а про мышление**\n\n"
        "Большинство джунов ошибочно считают, что DevOps — это:\n"
        "→ Docker + Kubernetes\n"
        "→ Ansible + Terraform\n"
        "→ CI/CD пайплайны\n\n"
        "Но настоящий DevOps — это:\n"
        "✅ Системное мышление: как части влияют на целое\n"
        "✅ Ответственность за продукт от идеи до продакшена\n"
        "✅ Культура, где ошибка — это возможность для роста\n\n"
        "🔥 Ключевая метрика успеха: **MTTR (Mean Time To Recovery)** —\n"
        "сколько времени уходит на восстановление после сбоя.\n"
        "Не MTBF (Mean Time Between Failures) — ломаться всё равно будет.\n\n"
        "💡 Dareira учит именно системному мышлению, а не кнопкам в интерфейсе."
    )
    
    await callback.message.answer(
        article_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Вернуться к урокам", callback_data="back_to_modules")]
        ])
    )
    await callback.answer()
