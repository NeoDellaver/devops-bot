import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
MODEL_URI = os.getenv("MODEL_URI", "gpt://<ваш_каталог>/yandexgpt-lite/latest")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/users.db")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))  # Замени на свой ID!
# ID вашего канала (можно @username или числовой ID)
CHANNEL_ID = "@devvvops"  # Например: "@devops_dareira"
STAR_PRICE = 990
