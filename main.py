
# coding: utf-8

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import os

steps = [
    {'step': 1, 'positions': [{'duration_min': 1.5}]},
    {'step': 2, 'positions': [{'duration_min': 2.0}]},
    {'step': 3, 'positions': [{'duration_min': 3.0}]}
]

API_TOKEN = os.getenv("TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def generate_wide_label(step_num, total):
    if total >= 60:
        return f"Шаг {step_num} — {int(total // 60)} ч {int(total % 60)} мин"
    return f"Шаг {step_num} — {int(total)} мин"

def steps_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = []
    for s in steps:
        step_num = s['step']
        total = sum(p['duration_min'] for p in s['positions'])
        label = generate_wide_label(step_num, total)
        buttons.append(KeyboardButton(label))
    kb.add(*buttons)
    kb.add(KeyboardButton("ℹ️ Инфо"))
    return kb

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    await msg.answer("Привет! Выбери шаг:", reply_markup=steps_keyboard())

@dp.message_handler(lambda m: m.text == "📋 Вернуться к шагам")
async def back_to_steps(msg: types.Message):
    await msg.answer("Вот меню шагов:", reply_markup=steps_keyboard())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
