# fix_premium_column.py
import aiosqlite
import asyncio

async def add_is_premium_column():
    async with aiosqlite.connect("devops_bot.db") as db:
        try:
            # Попробуем добавить колонку
            await db.execute("ALTER TABLE users ADD COLUMN is_premium BOOLEAN DEFAULT 0;")
            await db.commit()
            print("✅ Колонка 'is_premium' успешно добавлена.")
        except aiosqlite.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️ Колонка 'is_premium' уже существует.")
            else:
                print(f"❌ Ошибка: {e}")
        except Exception as e:
            print(f"💥 Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(add_is_premium_column())
