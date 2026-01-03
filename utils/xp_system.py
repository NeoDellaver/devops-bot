# utils/xp_system.py
import json
import os

STATUS_FILE = "data/statuses.json"

def get_status_by_xp(xp: int) -> str:
    with open(STATUS_FILE, encoding="utf-8") as f:
        statuses = json.load(f)
    for status in reversed(statuses):
        if xp >= status["xp_required"]:
            return status["name"]
    return "Новичок"