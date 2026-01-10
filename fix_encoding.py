#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления UTF-8 кодировки в начало всех Python файлов
Это необходимо для корректной работы на Linux сервере
"""

import os
import sys

def add_encoding_header(filepath):
    """Добавить UTF-8 заголовок в файл"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Если уже есть кодировка - пропустить
    if content.startswith('# -*- coding:') or content.startswith('#!/'):
        return False
    
    # Добавить кодировку в начало
    new_content = '# -*- coding: utf-8 -*-\n' + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    # Список файлов которые нужно исправить
    files_to_fix = [
        'config.py',
        'database.py', 
        'dareira_api.py',
        'handlers/start.py',
        'handlers/modules.py',
        'handlers/dareira.py',
        'handlers/admin.py',
        'handlers/progress.py',
        'utils/xp_system.py',
    ]
    
    fixed_count = 0
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            try:
                if add_encoding_header(filepath):
                    print(f"✅ Исправлен: {filepath}")
                    fixed_count += 1
                else:
                    print(f"⏭️ Уже исправлен: {filepath}")
            except Exception as e:
                print(f"❌ Ошибка в {filepath}: {e}")
        else:
            print(f"⚠️ Не найден: {filepath}")
    
    print(f"\n✅ Исправлено файлов: {fixed_count}")

if __name__ == '__main__':
    main()
