# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
MODEL_URI = os.getenv("MODEL_URI", "gpt://b1gm6ba1aebp0vf17r9o/yandexgpt/rc")

YANDEX_GPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"