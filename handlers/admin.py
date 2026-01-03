# handlers/admin.py
import json
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import ADMIN_USER_ID

router = Router()

# Путь к данным
LESSONS_FILE = "data/lessons.json"

# Загружаем уроки
def load_lessons():
    with open(LESSONS_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_lessons(data):
    with open(LESSONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# FSM состояния
class AdminEdit(StatesGroup):
    waiting_for_module = State()
    waiting_for_lesson_number = State()
    waiting_for_field = State()
    waiting_for_new_value = State()
    waiting_for_new_lesson_data = State()  # для добавления

# Проверка админа
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_USER_ID

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 У вас нет доступа к админке.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать урок", callback_data="admin:edit")],
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data="admin:add")],
        [InlineKeyboardButton(text="🔄 Обновить данные", callback_data="admin:reload")]
    ])
    await message.answer("🛠️ Панель администратора", reply_markup=kb)

# === РЕДАКТИРОВАНИЕ ===
@router.callback_query(F.data == "admin:edit")
async def edit_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    lessons = load_lessons()
    modules = list(lessons.keys())
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m, callback_data=f"admin:module:{m}")] for m in modules
    ] + [[InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back")]]
    )
    await callback.message.edit_text("Выберите модуль для редактирования:", reply_markup=kb)
    await state.set_state(AdminEdit.waiting_for_module)

@router.callback_query(F.data.startswith("admin:module:"))
async def choose_lesson_number(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    module = callback.data.split(":")[2]
    lessons = load_lessons()
    lesson_list = lessons.get(module, [])
    if not lesson_list:
        await callback.message.edit_text("В этом модуле нет уроков.")
        return
    opts = [
        [InlineKeyboardButton(text=f"Урок {i+1}: {lesson['title']}", callback_data=f"admin:lesson:{module}:{i}")]
        for i, lesson in enumerate(lesson_list)
    ]
    opts.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin:edit")])
    await callback.message.edit_text(f"Модуль: {module}\nВыберите урок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=opts))
    await state.update_data(module=module)
    await state.set_state(AdminEdit.waiting_for_lesson_number)

@router.callback_query(F.data.startswith("admin:lesson:"))
async def choose_field(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    parts = callback.data.split(":")
    module = parts[2]
    lesson_idx = int(parts[3])
    await state.update_data(module=module, lesson_idx=lesson_idx)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Название", callback_data="admin:field:title")],
        [InlineKeyboardButton(text="📄 Содержание", callback_data="admin:field:content")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"admin:module:{module}")]
    ])
    await callback.message.edit_text("Что хотите изменить?", reply_markup=kb)
    await state.set_state(AdminEdit.waiting_for_field)

@router.callback_query(F.data.startswith("admin:field:"))
async def enter_new_value(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    field = callback.data.split(":")[2]
    await state.update_data(field=field)
    await callback.message.edit_text(f"Введите новое значение для поля '{field}':")
    await state.set_state(AdminEdit.waiting_for_new_value)

@router.message(AdminEdit.waiting_for_new_value)
async def save_new_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    module = data["module"]
    lesson_idx = data["lesson_idx"]
    field = data["field"]
    new_value = message.text

    lessons = load_lessons()
    lessons[module][lesson_idx][field] = new_value
    save_lessons(lessons)

    await message.answer("✅ Урок обновлён!")
    await state.clear()
    # Вернуть в админку
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать ещё", callback_data="admin:edit")],
        [InlineKeyboardButton(text="🛠️ Админка", callback_data="admin:back")]
    ])
    await message.answer("Что дальше?", reply_markup=kb)

# === ДОБАВЛЕНИЕ УРОКА ===
@router.callback_query(F.data == "admin:add")
async def add_lesson_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    lessons = load_lessons()
    modules = list(lessons.keys())
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=m, callback_data=f"admin:add_module:{m}")] for m in modules
    ] + [[InlineKeyboardButton(text="🔙 Назад", callback_data="admin:back")]]
    )
    await callback.message.edit_text("Выберите модуль для добавления урока:", reply_markup=kb)

@router.callback_query(F.data.startswith("admin:add_module:"))
async def add_lesson_title(callback: CallbackQuery, state: FSMContext):
    module = callback.data.split(":")[2]
    await state.update_data(module=module, step="title")
    await callback.message.edit_text("Введите название нового урока:")

@router.message(F.text)
async def add_lesson_content_or_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    current_state = await state.get_state()
    if current_state not in [None, ""]:
        return  # Чтобы не мешало основному боту

    data = await state.get_data()
    step = data.get("step")
    module = data.get("module")

    if step == "title":
        await state.update_data(title=message.text, step="content")
        await message.answer("Введите содержание урока:")
    elif step == "content":
        lessons = load_lessons()
        new_lesson = {
            "title": data["title"],
            "content": message.text,
            "questions": []  # можно расширить позже
        }
        lessons[module].append(new_lesson)
        save_lessons(lessons)
        await message.answer("✅ Новый урок добавлен!")
        await state.clear()

# === НАЗАД В АДМИНКУ ===
@router.callback_query(F.data == "admin:back")
async def back_to_admin(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать урок", callback_data="admin:edit")],
        [InlineKeyboardButton(text="➕ Добавить урок", callback_data="admin:add")],
        [InlineKeyboardButton(text="🔄 Обновить данные", callback_data="admin:reload")]
    ])
    await callback.message.edit_text("🛠️ Панель администратора", reply_markup=kb)