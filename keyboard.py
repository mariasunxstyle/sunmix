# keyboard.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from steps import steps
from utils import format_duration

# Кнопки шагов с таймингом
steps_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for step in steps:
    total = sum(pos[1] for pos in step["positions"])
    label = f"Шаг {step['step']} ({format_duration(total)})"
    steps_kb.insert(KeyboardButton(label))
steps_kb.add(KeyboardButton("ℹ️ Инфо"))

# Кнопки управления
control_kb = ReplyKeyboardMarkup(resize_keyboard=True)
control_kb.add(KeyboardButton("⏭️ Пропустить"))
control_kb.add(KeyboardButton("📋 Вернуться к шагам"))
control_kb.add(KeyboardButton("↩️ Назад на 2 шага"))
control_kb.add(KeyboardButton("⛔ Завершить"))

done_kb = ReplyKeyboardMarkup(resize_keyboard=True)
done_kb.add(
    KeyboardButton("▶️ Продолжить"),
    KeyboardButton("📋 Вернуться к шагам"),
    KeyboardButton("↩️ Назад на 2 шага"),
    KeyboardButton("⛔ Завершить")
)
