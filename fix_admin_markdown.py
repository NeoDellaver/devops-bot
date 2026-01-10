#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматически добавить parse_mode="Markdown" ко всем message.answer в admin.py
"""

import re

filepath = 'handlers/admin.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Если это строка с await и message.answer(
    if 'await' in line and 'message.answer(' in line:
        # Проверяем однострочный ли вызов
        if ')' in line:
            # Однострочный вызов
            if 'parse_mode' not in line:
                # Добавляем parse_mode перед )
                line = line.rstrip()
                if line.endswith(')'):
                    line = line[:-1] + ', parse_mode="Markdown")\n'
                else:
                    line = line + ', parse_mode="Markdown")'
            new_lines.append(line)
            i += 1
        else:
            # Многострочный вызов
            call_lines = [line]
            j = i + 1
            
            # Собираем до закрывающей скобки
            while j < len(lines) and ')' not in lines[j]:
                call_lines.append(lines[j])
                j += 1
            
            if j < len(lines):
                call_lines.append(lines[j])
            
            # Проверяем, есть ли parse_mode в вызове
            call_text = ''.join(call_lines)
            if 'parse_mode' not in call_text:
                # Добавляем перед закрывающей скобкой
                last_line = call_lines[-1]
                if last_line.strip() == ')':
                    indent = len(last_line) - len(last_line.lstrip())
                    call_lines.insert(-1, ' ' * indent + 'parse_mode="Markdown",\n')
                else:
                    # Закрывающая скобка на той же строке
                    call_lines[-1] = last_line.rstrip()[:-1] + ', parse_mode="Markdown")\n'
            
            new_lines.extend(call_lines)
            i = j + 1
    else:
        new_lines.append(line)
        i += 1

new_content = ''.join(new_lines)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ admin.py - добавлены parse_mode ко всем message.answer")
