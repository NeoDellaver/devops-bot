import requests
import json
import os
import logging
from config import YANDEX_API_KEY, MODEL_URI

logger = logging.getLogger(__name__)

def ask_dareira(question: str) -> str:
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Ты — Dareira, саркастичный DevOps-ментор в стиле Рика из «Рика и Морти».\n"
        "Отвечай коротко, по делу, на русском языке.\n"
        "Добавляй 1-2 технических детали, если уместно.\n"
        "Используй эмодзи только в начале/конце сообщения.\n"
        "Не пиши длинные вступления — сразу суть."
    )

    payload = {
        "modelUri": MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": f"Вопрос: {question}"}
        ]
    }

    try:
        # ИСПРАВЛЕНО: УБРАНЫ ПРОБЕЛЫ В URL!
        resp = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            json=payload,
            headers=headers,
            timeout=15
        )

        if resp.status_code == 200:
            text = resp.json()["result"]["alternatives"][0]["message"]["text"].strip()
            return text if text else "Даже мой AI-мозг не смог ответить на это... Попробуй переформулировать 😎"
        else:
            error_msg = f"Ошибка Yandex API: {resp.status_code}"
            logger.error(f"Yandex API error {resp.status_code}: {resp.text}")
            return error_msg
    except Exception as e:
        logger.exception("Исключение в ask_dareira")
        return f"Что-то сломалось в космосе: {str(e)}"


def dareira_rewrite(original_text: str, style_prompt: str) -> str:
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": MODEL_URI,
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,
            "maxTokens": 1500
        },
        "messages": [
            {"role": "system", "text": style_prompt},
            {"role": "user", "text": f"Перепиши ТОЛЬКО текст ниже в указанном стиле. НЕ ДОБАВЛЯЙ ничего от себя:\n\n{original_text}"}
        ]
    }

    try:
        # ИСПРАВЛЕНО: УБРАНЫ ПРОБЕЛЫ В URL!
        resp = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            json=payload,
            headers=headers,
            timeout=30
        )

        if resp.status_code == 200:
            text = resp.json()["result"]["alternatives"][0]["message"]["text"].strip()
            text = text.lstrip("*# \n").rstrip("*# \n")
            return text if text else "ИИ вернул пустой результат. Попробуйте другую тему."
        else:
            error_msg = f"Yandex API error {resp.status_code}"
            logger.error(f"Yandex error {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        logger.exception("Исключение в dareira_rewrite")
        return None
