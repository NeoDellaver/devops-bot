# test_yandex_api.py
import requests
import json
from config import YANDEX_API_KEY, MODEL_URI

# Проверка конфигурации
if not YANDEX_API_KEY or not MODEL_URI:
    print("❌ ОШИБКА: YANDEX_API_KEY или MODEL_URI не заданы в config.py")
    exit(1)

print("✅ Конфигурация загружена")
print(f"MODEL_URI: {MODEL_URI}")

# Тестовый запрос
headers = {
    "Authorization": f"Api-Key {YANDEX_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "modelUri": MODEL_URI,
    "completionOptions": {
        "stream": False,
        "temperature": 0.7,
        "maxTokens": 50
    },
    "messages": [
        {"role": "system", "text": "Ты — Dareira, DevOps-ментор."},
        {"role": "user", "text": "Привет! Напиши коротко о Docker."}
    ]
}

print("\n🔍 Отправляем запрос к Yandex API...")

try:
    resp = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        json=payload,
        headers=headers,
        timeout=15
    )
    
    print(f"Статус ответа: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        text = result["result"]["alternatives"][0]["message"]["text"]
        print(f"\n✅ УСПЕХ! Ответ ИИ:\n{text}")
    else:
        print(f"\n❌ ОШИБКА API: {resp.status_code}")
        print(f"Тело ответа: {resp.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ОШИБКА СЕТИ: Не удаётся подключиться к Yandex API")
    print("Возможно, сервер заблокирован или недоступен из вашей сети")
    
except requests.exceptions.Timeout:
    print("\n❌ ТАЙМАУТ: Yandex API не ответил за 15 секунд")
    
except Exception as e:
    print(f"\n❌ НЕИЗВЕСТНАЯ ОШИБКА: {e}")
