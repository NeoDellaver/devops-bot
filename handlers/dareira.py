from aiogram import Router, F
from aiogram.types import Message
from dareira_api import ask_dareira

router = Router()

@router.message(F.text.startswith("/dareira"))
async def dareira_command(message: Message):
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
    
    await message.answer("⏳ Думаю...")
    answer = ask_dareira(question)
    await message.answer(answer)
