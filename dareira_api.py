# dareira_api.py
import aiohttp
import logging

from config import YANDEX_API_KEY, MODEL_URI, YANDEX_GPT_API_URL

logger = logging.getLogger(__name__)

async def ask_dareira(prompt: str) -> str:
    if not YANDEX_API_KEY:
        return "❌ API-ключ Yandex GPT не настроен."

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 500
        },
        "messages": [
            {
                "role": "system",
                "text": (
                    "Ты — AI-ассистент по DevOps по имени Dareira. "
                    "Ты помогаешь пользователям понять темы Linux, Docker, Kubernetes, Ansible и базы данных. "
                    "Отвечай кратко, по делу, на русском языке. "
                    "Если вопрос не по теме DevOps — вежливо откажись и предложи задать вопрос по обучению."
                )
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_GPT_API_URL, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["result"]["alternatives"][0]["message"]["text"].strip()
                else:
                    error_text = await resp.text()
                    logger.error(f"Yandex GPT error {resp.status}: {error_text}")
                    return f"⚠️ Ошибка Yandex GPT ({resp.status}). Проверь API-ключ."
    except Exception as e:
        logger.exception("Ошибка при вызове Yandex GPT")
        return f"❌ Не удалось связаться с Dareira: {str(e)}"
        
