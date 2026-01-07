# database.py
import aiosqlite

DB_PATH = "devops_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                xp INTEGER DEFAULT 0,
                current_module TEXT DEFAULT 'linux',
                current_lesson INTEGER DEFAULT 0,
                completed_lessons TEXT DEFAULT '[]',
                is_premium BOOLEAN DEFAULT 0  -- ДОБАВЛЕНО
            )
        """)
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row

async def create_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username or "")
        )
        await db.commit()

async def update_user_progress(user_id: int, module: str, lesson: int, xp: int, completed: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users
            SET current_module = ?, current_lesson = ?, xp = xp + ?, completed_lessons = ?
            WHERE user_id = ?
        """, (module, lesson, xp, completed, user_id))
        await db.commit()
        
async def is_user_premium(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT is_premium FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return bool(row[0]) if row else False        

async def set_user_premium(user_id: int, is_premium: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_premium = ? WHERE user_id = ?",
            (int(is_premium), user_id)
        )
        await db.commit()
