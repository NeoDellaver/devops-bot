#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Заменить ** на ничего (или _) для правильного отображения в Markdown
"""

import json

filepath = 'data/lessons.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

for module_name in data:
    for lesson in data[module_name]:
        if 'content' in lesson and lesson['content']:
            # Заменяем ** на просто текст (удаляем маркеры)
            lesson['content'] = lesson['content'].replace('**', '')

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Все ** удалены из lessons.json")
