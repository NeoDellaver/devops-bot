import os

files = ["start.py", "dareira.py", "admin.py", "progress.py", "restyle.py"]

for fname in files:
    fpath = f"handlers/{fname}"
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_answer = 'message.answer' in content
    has_pm = 'parse_mode' in content
    
    print(f"{fname:20} - message.answer: {has_answer!s:5} - parse_mode: {has_pm!s:5}")
