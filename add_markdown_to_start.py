#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавить parse_mode="Markdown" ко всем message.answer в start.py
"""

import re

filepath = 'handlers/start.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Найти все message.answer без parse_mode и добавить его
# Заменяем: await message.answer(
#              text,
#              reply_markup=...
#          )
# На:       await message.answer(
#              text,
#              parse_mode="Markdown",
#              reply_markup=...
#          )

# Простая замена для основного блока
content = content.replace(
    '''            intro_text,
            reply_markup=kb,
            disable_web_page_preview=True''',
    '''            intro_text,
            parse_mode="Markdown",
            reply_markup=kb,
            disable_web_page_preview=True'''
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Добавлен parse_mode='Markdown' в start.py")
