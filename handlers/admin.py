# handlers/admin.py
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
import json
import os
import logging
from config import ADMIN_USER_ID, CHANNEL_ID
from dareira_api import dareira_rewrite

logger = logging.getLogger(__name__)
router = Router()

LESSONS_PATH = "data/lessons.json"

def load_lessons():
    if not os.path.exists(LESSONS_PATH):
        return {}
    with open(LESSONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_lessons(lessons):
    os.makedirs("data", exist_ok=True)
    with open(LESSONS_PATH, "w", encoding="utf-8") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)

# FSM States
class AdminState(StatesGroup):
    # Модули
    waiting_for_module_name = State()
    # Уроки
    waiting_for_lesson_title = State()
    waiting_for_lesson_content = State()
    editing_lesson_content = State()
    # Вопросы
    waiting_for_question_text = State()
    waiting_for_question_options = State()
    waiting_for_correct_answer = State()
    # Удаление
    confirm_delete_lesson = State()
    confirm_delete_module = State()
    # НОВОЕ: для публикации статьи
    waiting_for_article_confirmation = State()

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def get_modules_keyboard(lessons):
    buttons = [
        [InlineKeyboardButton(text=f"📁 {module}", callback_data=f"admin_module:{module}")]
        for module in sorted(lessons.keys())
    ]
    buttons.append([InlineKeyboardButton(text="➕ Добавить модуль", callback_data="admin_new_module")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lessons_keyboard(module, lessons):
    buttons = [
        [InlineKeyboardButton(text=f"{i+1}. {lesson['title']}", callback_data=f"admin_lesson:{module}:{i}")]
        for i, lesson in enumerate(lessons[module])
    ]
    buttons.append([InlineKeyboardButton(text="➕ Добавить урок", callback_data=f"admin_new_lesson:{module}")])
    buttons.append([InlineKeyboardButton(text="🗑️ Удалить модуль", callback_data=f"admin_delete_module:{module}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back_to_modules")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_lesson_actions_keyboard(module, lesson_idx):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать текст", callback_data=f"admin_edit_content:{module}:{lesson_idx}")],
        [InlineKeyboardButton(text="❓ Управление вопросами", callback_data=f"admin_manage_questions:{module}:{lesson_idx}")],
        [InlineKeyboardButton(text="🗑️ Удалить урок", callback_data=f"admin_delete_lesson:{module}:{lesson_idx}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_module:{module}")]
    ])

def get_questions_keyboard(module, lesson_idx, questions):
    buttons = [
        [InlineKeyboardButton(text=f"Q{i+1}: {q['text'][:30]}...", callback_data=f"admin_question:{module}:{lesson_idx}:{i}")]
        for i, q in enumerate(questions)
    ]
    buttons.append([InlineKeyboardButton(text="➕ Добавить вопрос", callback_data=f"admin_new_question:{module}:{lesson_idx}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_lesson:{module}:{lesson_idx}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# === ОСНОВНОЕ МЕНЮ ===

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("🚫 Доступ запрещён.", parse_mode="Markdown")
        return
    await state.clear()
    lessons = load_lessons()
    await message.answer(
        "🛠️ <b>Админ-панель курса</b>\nВыберите модуль для управления:",
        parse_mode="HTML",
        reply_markup=get_modules_keyboard(lessons)
    )

# === НАВИГАЦИЯ ===

@router.callback_query(F.data == "admin_back_to_main")
async def admin_back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lessons = load_lessons()
    await callback.message.edit_text(
        "🛠️ <b>Админ-панель курса</b>\nВыберите модуль:",
        parse_mode="HTML",
        reply_markup=get_modules_keyboard(lessons)
    )
    await callback.answer()

@router.callback_query(F.data == "admin_back_to_modules")
async def admin_back_to_modules(callback: CallbackQuery, state: FSMContext):
    lessons = load_lessons()
    await callback.message.edit_text(
        "🛠️ <b>Админ-панель курса</b>\nВыберите модуль:",
        parse_mode="HTML",
        reply_markup=get_modules_keyboard(lessons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_module:"))
async def admin_select_module(callback: CallbackQuery, state: FSMContext):
    module = callback.data.split(":", 1)[1]
    lessons = load_lessons()
    if module not in lessons:
        await callback.answer("❌ Модуль не найден.")
        return
    await callback.message.edit_text(
        f"📚 Модуль: <b>{module}</b>\nВыберите урок:",
        parse_mode="HTML",
        reply_markup=get_lessons_keyboard(module, lessons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_lesson:"))
async def admin_view_lesson(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    lessons = load_lessons()
    if module not in lessons or lesson_idx >= len(lessons[module]):
        await callback.answer("❌ Урок не найден.")
        return
    lesson = lessons[module][lesson_idx]
    text = (
        f"📖 <b>{lesson['title']}</b>\n\n"
        f"{lesson['content']}\n\n"
        f"❓ Вопросов: {len(lesson['questions'])}"
    )
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_lesson_actions_keyboard(module, lesson_idx)
    )
    await callback.answer()

# === МОДУЛИ ===

@router.callback_query(F.data == "admin_new_module")
async def admin_new_module(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminState.waiting_for_module_name)
    await callback.message.answer("✏️ Введите название нового модуля (например, 'Безопасность'):", parse_mode="Markdown")
    await callback.answer()

@router.message(AdminState.waiting_for_module_name)
async def process_new_module_name(message: Message, state: FSMContext):
    module_name = message.text.strip()
    if not module_name:
        await message.answer("❌ Название не может быть пустым. Попробуйте снова:", parse_mode="Markdown")
        return
    lessons = load_lessons()
    if module_name in lessons:
        await message.answer(f"⚠️ Модуль '{module_name}' уже существует.", parse_mode="Markdown")
        return
    lessons[module_name] = []
    save_lessons(lessons)
    await message.answer(f"✅ Модуль '{module_name}' создан!", parse_mode="Markdown")
    await state.clear()
    await message.answer(
        "🛠️ <b>Админ-панель курса</b>\nВыберите модуль:",
        parse_mode="HTML",
        reply_markup=get_modules_keyboard(lessons)
    )

@router.callback_query(F.data.startswith("admin_delete_module:"))
async def admin_delete_module_confirm(callback: CallbackQuery, state: FSMContext):
    module = callback.data.split(":", 1)[1]
    lessons = load_lessons()
    count = len(lessons.get(module, []))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_module:{module}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back_to_modules")]
    ])
    await callback.message.edit_text(
        f"⚠️ Удалить модуль '{module}' и все {count} уроков?",
        reply_markup=kb
    )
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_module:"))
async def confirm_delete_module(callback: CallbackQuery, state: FSMContext):
    module = callback.data.split(":", 1)[1]
    lessons = load_lessons()
    if module in lessons:
        del lessons[module]
        save_lessons(lessons)
        await callback.message.edit_text(f"🗑️ Модуль '{module}' удалён.")
    else:
        await callback.message.edit_text("❌ Модуль не найден.")
    await callback.answer()

# === УРОКИ ===

@router.callback_query(F.data.startswith("admin_new_lesson:"))
async def admin_new_lesson(callback: CallbackQuery, state: FSMContext):
    module = callback.data.split(":", 1)[1]
    await state.update_data(current_module=module)
    await state.set_state(AdminState.waiting_for_lesson_title)
    await callback.message.answer("✏️ Введите название урока:", parse_mode="Markdown")
    await callback.answer()

@router.message(AdminState.waiting_for_lesson_title)
async def process_lesson_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if not title:
        await message.answer("❌ Название не может быть пустым.", parse_mode="Markdown")
        return
    await state.update_data(lesson_title=title)
    await state.set_state(AdminState.waiting_for_lesson_content)
    await message.answer("✏️ Введите текст урока (поддерживается Markdown):", parse_mode="Markdown")

@router.message(AdminState.waiting_for_lesson_content)
async def process_lesson_content(message: Message, state: FSMContext):
    content = message.text.strip()
    if not content:
        await message.answer("❌ Текст не может быть пустым.", parse_mode="Markdown")
        return
    data = await state.get_data()
    module = data["current_module"]
    title = data["lesson_title"]
    lessons = load_lessons()
    lessons[module].append({
        "title": title,
        "content": content,
        "questions": []
    })
    save_lessons(lessons)
    await message.answer(f"✅ Урок '{title}' добавлен!", parse_mode="Markdown")
    await state.clear()
    await message.answer(
        f"📚 Модуль: <b>{module}</b>\nВыберите урок:",
        parse_mode="HTML",
        reply_markup=get_lessons_keyboard(module, lessons)
    )

@router.callback_query(F.data.startswith("admin_edit_content:"))
async def admin_edit_content(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":")
    await state.update_data(edit_module=module, edit_lesson_idx=int(lesson_idx))
    await state.set_state(AdminState.editing_lesson_content)
    await callback.message.answer("✏️ Отправьте новый текст урока:", parse_mode="Markdown")
    await callback.answer()

@router.message(AdminState.editing_lesson_content)
async def process_edit_content(message: Message, state: FSMContext):
    new_content = message.text.strip()
    if not new_content:
        await message.answer("❌ Текст не может быть пустым.", parse_mode="Markdown")
        return
    data = await state.get_data()
    module = data["edit_module"]
    lesson_idx = data["edit_lesson_idx"]
    lessons = load_lessons()
    lessons[module][lesson_idx]["content"] = new_content
    save_lessons(lessons)
    await message.answer("✅ Текст урока обновлён!", parse_mode="Markdown")
    await state.clear()
    await message.answer(
        f"📚 Модуль: <b>{module}</b>\nВыберите урок:",
        parse_mode="HTML",
        reply_markup=get_lessons_keyboard(module, lessons)
    )

@router.callback_query(F.data.startswith("admin_delete_lesson:"))
async def admin_delete_lesson_confirm(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    lessons = load_lessons()
    title = lessons[module][lesson_idx]["title"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_lesson:{module}:{lesson_idx}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_lesson:{module}:{lesson_idx}")]
    ])
    await callback.message.edit_text(f"⚠️ Удалить урок '{title}'?", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("confirm_delete_lesson:"))
async def confirm_delete_lesson(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    lessons = load_lessons()
    if module in lessons and 0 <= lesson_idx < len(lessons[module]):
        title = lessons[module].pop(lesson_idx)["title"]
        save_lessons(lessons)
        await callback.message.edit_text(f"🗑️ Урок '{title}' удалён.")
    else:
        await callback.message.edit_text("❌ Урок не найден.")
    await callback.answer()

# === ВОПРОСЫ ===

@router.callback_query(F.data.startswith("admin_manage_questions:"))
async def admin_manage_questions(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    lessons = load_lessons()
    questions = lessons[module][lesson_idx]["questions"]
    await callback.message.edit_text(
        f"❓ Вопросы к уроку\nВсего: {len(questions)}",
        reply_markup=get_questions_keyboard(module, lesson_idx, questions)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("admin_new_question:"))
async def admin_new_question_start(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx = callback.data.split(":")
    await state.update_data(q_module=module, q_lesson_idx=int(lesson_idx))
    await state.set_state(AdminState.waiting_for_question_text)
    await callback.message.answer("✏️ Введите текст вопроса:", parse_mode="Markdown")
    await callback.answer()

@router.message(AdminState.waiting_for_question_text)
async def process_question_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("❌ Текст вопроса не может быть пустым.", parse_mode="Markdown")
        return
    await state.update_data(question_text=text)
    await state.set_state(AdminState.waiting_for_question_options)
    await message.answer("✏️ Введите варианты ответов, каждый с новой строки:\n\nПример:\nDocker\nKubernetes\nAnsible\nTerraform", parse_mode="Markdown")

@router.message(AdminState.waiting_for_question_options)
async def process_question_options(message: Message, state: FSMContext):
    options = [opt.strip() for opt in message.text.strip().split("\n") if opt.strip()]
    if len(options) < 2:
        await message.answer("❌ Нужно минимум 2 варианта. Попробуйте снова:", parse_mode="Markdown")
        return
    await state.update_data(question_options=options)
    await state.set_state(AdminState.waiting_for_correct_answer)
    opts_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    await message.answer(f"✅ Варианты:\n{opts_text}\n\n✏️ Введите номер правильного ответа (1-{len(options)}):", parse_mode="Markdown")

@router.message(AdminState.waiting_for_correct_answer)
async def process_correct_answer(message: Message, state: FSMContext):
    try:
        correct_idx = int(message.text.strip()) - 1
    except ValueError:
        await message.answer("❌ Введите число. Попробуйте снова:", parse_mode="Markdown")
        return
    data = await state.get_data()
    options = data["question_options"]
    if correct_idx < 0 or correct_idx >= len(options):
        await message.answer(f"❌ Номер должен быть от 1 до {len(options)}. Попробуйте снова:", parse_mode="Markdown")
        return
    module = data["q_module"]
    lesson_idx = data["q_lesson_idx"]
    lessons = load_lessons()
    lessons[module][lesson_idx]["questions"].append({
        "text": data["question_text"],
        "options": options,
        "correct": correct_idx
    })
    save_lessons(lessons)
    await message.answer("✅ Вопрос добавлен!", parse_mode="Markdown")
    await state.clear()
    questions = lessons[module][lesson_idx]["questions"]
    await message.answer(
        f"❓ Вопросы к уроку\nВсего: {len(questions)}", parse_mode="Markdown")
        reply_markup=get_questions_keyboard(module, lesson_idx, questions)
    )

@router.callback_query(F.data.startswith("admin_question:"))
async def admin_view_question(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx, q_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    q_idx = int(q_idx)
    lessons = load_lessons()
    q = lessons[module][lesson_idx]["questions"][q_idx]
    opts = "\n".join([f"{'✅' if i == q['correct'] else '❌'} {opt}" for i, opt in enumerate(q["options"])])
    text = f"❓ <b>{q['text']}</b>\n\n{opts}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑️ Удалить вопрос", callback_data=f"admin_delete_question:{module}:{lesson_idx}:{q_idx}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_manage_questions:{module}:{lesson_idx}")]
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_delete_question:"))
async def admin_delete_question(callback: CallbackQuery, state: FSMContext):
    _, module, lesson_idx, q_idx = callback.data.split(":")
    lesson_idx = int(lesson_idx)
    q_idx = int(q_idx)
    lessons = load_lessons()
    q = lessons[module][lesson_idx]["questions"].pop(q_idx)
    save_lessons(lessons)
    await callback.message.edit_text("🗑️ Вопрос удалён.")
    await callback.answer()

# === НОВОЕ: ПУБЛИКАЦИЯ СТАТЬИ В КАНАЛ ===

@router.message(Command("topost"))
async def cmd_topost(message: Message, state: FSMContext, bot: Bot):
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("🚫 Только для админа", parse_mode="Markdown")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Укажи тему после команды.\nПример: `/topost Как я убил 3 бага`",
            parse_mode="Markdown"
        )
        return

    topic = args[1].strip()
    await message.answer(f"🎨 Генерирую статью на тему: {topic}...", parse_mode="Markdown")

    try:
        if not os.path.exists("data/author_style.txt"):
            await message.answer("❌ Не найден файл стиля: data/author_style.txt", parse_mode="Markdown")
            return

        with open("data/author_style.txt", "r", encoding="utf-8") as f:
            style_prompt = f.read().strip()

        if not style_prompt:
            await message.answer("❌ Файл стиля пуст!", parse_mode="Markdown")
            return

        prompt = (
            f"Ты — Dareira, саркастичный DevOps-гуру в стиле Рика из «Рика и Морти».\n"
            f"Напиши короткую ИРОНИЧНУЮ статью на тему: «{topic}».\n"
            "Даже если тема не техническая — свяжи её с DevOps/программированием.\n"
            "Правила:\n"
            "- Максимум 5 предложений\n"
            "- Обязательно добавь 1-2 технические детали (Linux, Docker, CI/CD и т.д.)\n"
            "- В конце 3 совета в нумерованном списке\n"
            "- Хештеги: #DevOps #Dareira"
        )

        article = dareira_rewrite(prompt, style_prompt)

        if not article or len(article) < 20:
            await message.answer("❌ Не удалось сгенерировать статью. Попробуйте другую тему.", parse_mode="Markdown")
            return

        await state.update_data(article_to_post=article)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Отправить в канал", callback_data="publish_to_channel")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_publish")]
        ])

        await message.answer(
            f"✅ **ГОТОВО!**\n\n{article}",
            parse_mode="Markdown",
            reply_markup=kb
        )
        await state.set_state(AdminState.waiting_for_article_confirmation)

    except Exception as e:
        logger.exception("Ошибка в /topost")
        await message.answer(f"❌ Ошибка генерации: {str(e)}", parse_mode="Markdown")


@router.callback_query(F.data == "publish_to_channel")
async def publish_to_channel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    article = data.get("article_to_post")
    
    if not article:
        await callback.message.edit_text("❌ Статья не найдена.")
        await state.clear()
        return

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=article,
            parse_mode="Markdown"
        )
        await callback.message.edit_text("🚀 **Статья опубликована в канал!**")
    except Exception as e:
        logger.exception("Ошибка публикации в канал")
        await callback.message.edit_text(f"❌ Не удалось опубликовать в канал:\n{str(e)}")
    
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_publish")
async def cancel_publish(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Публикация отменена.")
    await callback.answer()

# === ПЕРЕЗАПУСК БОТА ===

import os

@router.message(Command("reboot"))
async def cmd_reboot(message: Message):
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("🚫 Доступ запрещён.", parse_mode="Markdown")
        return

    await message.answer("🔄 Бот перезапускается...", parse_mode="Markdown")
    logger.info(f"Админ {message.from_user.id} инициировал перезагрузку.")
    os._exit(0)
