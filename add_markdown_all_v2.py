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
    
    # Регулярное выражение для поиска await message.answer или await callback.message.answer
    # без parse_mode
    
    # Паттерн: await (callback.)message.answer(\n...\n) без parse_mode внутри
    pattern = r'(await (?:callback\.)?message\.answer\(\s*)((?:[^,)]*,\s*)*?)([^)]*\))'
    
    def add_parse_mode(match):
        prefix = match.group(1)  # await message.answer(
        content_before = match.group(2)  # параметры до
        rest = match.group(3)  # остаток до )
        
        # Проверяем, есть ли уже parse_mode в всё вызове
        full_call = prefix + content_before + rest
        if 'parse_mode' in full_call:
            return full_call
        
        # Находим первый аргумент (обычно текст)
        # Добавляем parse_mode="Markdown", после первого аргумента
        
        first_arg_end = content_before.find(',')
        if first_arg_end == -1:
            # Нет запятой - это однострочный вызов или текст последний параметр
            # Добавляем parse_mode перед закрывающей скобкой
            if rest.strip() == ')':
                return prefix + content_before + '\n            parse_mode="Markdown"' + rest
            return full_call
        else:
            # Добавляем parse_mode после первого параметра
            first_arg = content_before[:first_arg_end]
            rest_params = content_before[first_arg_end:]
            return prefix + first_arg + ',\n            parse_mode="Markdown"' + rest_params + rest
    
    # Более простой подход: заменить построчно
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Если это строка с await message.answer(
        if 'await' in line and 'message.answer(' in line:
            # Собираем весь вызов
            call_lines = [line]
            j = i + 1
            
            # Собираем все строки до закрытия )
            while j < len(lines) and ')' not in lines[j]:
                call_lines.append(lines[j])
                j += 1
            
            if j < len(lines):
                call_lines.append(lines[j])
            
            call_text = '\n'.join(call_lines)
            
            # Проверяем, есть ли parse_mode в вызове
            if 'parse_mode' not in call_text and 'reply_markup' not in call_text:
                # Добавляем parse_mode прямо в первую строку если она однострочная
                if len(call_lines) == 1 and '(' in line and ')' in line:
                    # Однострочный вызов: await message.answer("text")
                    new_line = line.replace(')', ', parse_mode="Markdown")')
                    result_lines.append(new_line)
                    i = j + 1
                    continue
                elif len(call_lines) > 1:
                    # Многострочный вызов
                    result_lines.extend(call_lines[:-1])  # Добавляем все кроме последней строки
                    
                    # Проверяем последнюю строку (где должна быть закрывающая скобка)
                    last_line = call_lines[-1]
                    
                    # Добавляем parse_mode перед закрывающей скобкой
                    indent = len(last_line) - len(last_line.lstrip())
                    if last_line.strip() == ')':
                        result_lines.append(' ' * indent + 'parse_mode="Markdown",')
                        result_lines.append(last_line)
                    else:
                        result_lines.append(last_line.replace(')', ', parse_mode="Markdown")'))
                    
                    i = j + 1
                    continue
        
        result_lines.append(line)
        i += 1
    
    new_content = '\n'.join(result_lines)
    
    if new_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ {filename}")
    else:
        print(f"⚠️  {filename} - требуется ручная проверка")

print("\n✅ Обновление завершено!")
