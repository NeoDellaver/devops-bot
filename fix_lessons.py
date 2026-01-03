import json

# Вставьте ВАШИ данные здесь в виде Python-словаря
lessons_data = {
    "linux": [
        {
            "title": "Загрузка Linux: от кнопки питания до рабочей системы",
            "content": "Процесс загрузки Linux включает несколько этапов:\n\n1. **BIOS/UEFI** выполняет POST и выбирает загрузочное устройство. BIOS использует MBR (до 2.2 ТБ), UEFI — GPT (до 9.4 ЗБ) и поддерживает Secure Boot.\n\n2. **Загрузчик (GRUB)** читает `/boot/grub/grub.cfg`, загружает ядро (`vmlinuz`) и initramfs.\n\n3. **Ядро** инициализирует оборудование, монтирует корневую ФС. **initramfs** содержит драйверы для LVM, RAID, шифрования.\n\n4. **Init-процесс** (PID 1): раньше SysVinit, сейчас systemd (параллельный запуск, юниты, journalctl).\n\n5. **PID 0** — swapper (idle process), **PID 1** — init/systemd (родитель всех процессов).\n\n6. **PXE** — загрузка по сети: клиент получает IP от DHCP, затем загружает образ по TFTP.\n\nЭтапы критичны для диагностики \"не загружается сервер\" и настройки безопасной загрузки.",
            "questions": [
                {
                    "text": "Как происходит процесс загрузки ОС Linux с момента нажатия кнопки питания?",
                    "options": ["Ядро запускается первым", "BIOS/UEFI выполняет POST и инициализацию", "systemd стартует сразу", "Загрузчик работает без участия firmware"],
                    "correct": 1
                },
                {
                    "text": "Что такое BIOS и UEFI? Основное различие:",
                    "options": ["UEFI работает только в облаке", "BIOS поддерживает диски до 2.2 ТБ, UEFI — до 9.4 ЗБ", "BIOS использует GPT", "UEFI медленнее BIOS"],
                    "correct": 1
                },
                {
                    "text": "Что такое systemd и init? Основное преимущество systemd:",
                    "options": ["systemd медленнее", "systemd запускает сервисы параллельно", "init поддерживает только графический интерфейс", "systemd не умеет логировать"],
                    "correct": 1
                },
                {
                    "text": "Как понять, используется ли в системе systemd?",
                    "options": ["`ls /etc/init.d`", "`ps -p 1 -o comm=`", "`cat /etc/passwd`", "`uname -r`"],
                    "correct": 1
                },
                {
                    "text": "Что такое ядро, initramfs, загрузчик?",
                    "options": ["initramfs — это основной init-процесс", "Загрузчик монтирует корневую ФС", "initramfs — временная ФС для загрузки драйверов", "Ядро не управляет процессами"],
                    "correct": 2
                },
                {
                    "text": "Что такое PXE и как загрузиться по сети?",
                    "options": ["PXE — протокол шифрования", "PXE использует DHCP и TFTP для загрузки", "PQE работает только с Windows", "PXE не поддерживается в облаке"],
                    "correct": 1
                },
                {
                    "text": "Что за процессы в Linux с PID 0 и 1?",
                    "options": ["PID 0 — systemd, PID 1 — ядро", "PID 0 — swapper (idle), PID 1 — init/systemd", "PID 0 — GRUB, PID 1 — ядро", "PID 0 не существует"],
                    "correct": 1
                }
            ]
        },
        # ... остальные уроки (я добавлю их ниже)
    ],
    "databases": [],
    "ansible": [],
    "docker": [],
    "kubernetes": [],
    "module6": []
}

# Создаём папку data
import os
os.makedirs("data", exist_ok=True)

# Записываем в файл
with open("data/lessons.json", "w", encoding="utf-8") as f:
    json.dump(lessons_data, f, ensure_ascii=False, indent=2)

print("✅ lessons.json успешно создан и гарантированно валиден!")