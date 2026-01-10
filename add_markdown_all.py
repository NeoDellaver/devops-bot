#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавить parse_mode="Markdown" ко всем message.answer() во всех handler файлах
"""

import os
import re

handlers_dir = 'handlers'
files_to_process = ['start.py', 'modules.py', 'dareira.py', 'admin.py', 'progress.py', 'restyle.py']

for filename in files_to_process:
    filepath = os.path.join(handlers_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"⚠️  {filename} не найден")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Найти все await message.answer( без parse_mode и добавить его
    # Используем регулярные выражения для безопасной замены
    
    # Паттерн 1: await message.answer(\n            text,\n            ...
    # Заменяем на: await message.answer(\n            text,\n            parse_mode="Markdown",\n            ...
    
    # Простой способ: если уже есть parse_mode - пропускаем
    # Иначе добавляем после первого параметра (обычно текст)
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Ищем await message.answer(
        if 'await message.answer(' in line and 'parse_mode' not in line:
            new_lines.append(line)
            i += 1
            
            # Ищем следующую строку с параметром
            if i < len(lines):
                next_line = lines[i]
                # Это обычно текст или первый параметр
                new_lines.append(next_line)
                i += 1
                
                # Проверяем, есть ли уже parse_mode в следующих строках до закрытия )
                has_parse_mode = False
                j = i
                while j < len(lines) and ')' not in lines[j]:
                    if 'parse_mode' in lines[j]:
                        has_parse_mode = True
                        break
                    j += 1
                
                # Если нет parse_mode, добавляем его
                if not has_parse_mode and i < len(lines):
                    current_line = lines[i]
                    # Проверяем, не конец ли это вызова
                    if current_line.strip() and not current_line.strip().startswith(')'):
                        # Добавляем parse_mode="Markdown", перед следующим параметром
                        indent = len(current_line) - len(current_line.lstrip())
                        new_lines.append(' ' * indent + 'parse_mode="Markdown",')
        else:
            new_lines.append(line)
            i += 1
    
    new_content = '\n'.join(new_lines)
    
    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ {filename} - добавлен parse_mode")
    else:
        print(f"ℹ️  {filename} - изменений не требуется")

print("\n✅ Готово!")
