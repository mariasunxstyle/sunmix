# coding: utf-8

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import os

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@sunxstyle"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

steps = [
    {"step": i, "positions": [
        {"name": "Лицом вверх", "duration_min": 0.1},
        {"name": "На животе", "duration_min": 0.1},
        {"name": "Левый бок", "duration_min": 0.1},
        {"name": "Правый бок", "duration_min": 0.1},
        {"name": "В тени", "duration_min": 0.1},
    ]} for i in range(1, 13)
]

user_states = {}

def steps_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        KeyboardButton(f"Шаг {s['step']} — {int(sum(p['duration_min'] for p in s['positions']))} мин") for s in steps
    ]
    kb.add(*buttons)
    kb.add(KeyboardButton("ℹ️ Инфо"))
    return kb

def control_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("⏭️ Пропустить"))
    kb.add(KeyboardButton("⛔ Завершить"))
    kb.add(KeyboardButton("↩️ Назад на 2 шага (если был перерыв)"))
    kb.add(KeyboardButton("📋 Вернуться к шагам"))
    return kb

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    await msg.answer("Привет! Выбери шаг:", reply_markup=steps_keyboard())

@dp.message_handler(lambda m: m.text and m.text.startswith("Шаг "))
async def handle_step(msg: types.Message):
    try:
        step_num = int(msg.text.split()[1])
        step_data = next((s for s in steps if s["step"] == step_num), None)
        if not step_data:
            return await msg.answer("Шаг не найден")
        user_states[msg.from_user.id] = {"step": step_num, "pos": 0}
        pos = step_data["positions"][0]
        await msg.answer(f"{pos['name']} — {pos['duration_min']} мин", reply_markup=control_keyboard())
        await start_timer(msg.chat.id, msg.from_user.id)
    except:
        await msg.answer("Что-то пошло не так")

@dp.message_handler(lambda m: m.text in ["📋 Вернуться к шагам", "⛔ Завершить", "⏭️ Пропустить", "↩️ Назад на 2 шага (если был перерыв)"])
async def handle_controls(msg: types.Message):
    user = user_states.get(msg.from_user.id)
    if msg.text == "📋 Вернуться к шагам":
        await msg.answer("Вот меню шагов:", reply_markup=steps_keyboard())
    elif msg.text == "⛔ Завершить":
        await msg.answer("Сеанс завершён. Вернись позже ☀️", reply_markup=steps_keyboard())
        user_states.pop(msg.from_user.id, None)
    elif msg.text == "⏭️ Пропустить" and user:
        user["pos"] += 1
        await continue_step(msg.chat.id, msg.from_user.id)
    elif msg.text == "↩️ Назад на 2 шага (если был перерыв)" and user:
        user["step"] = max(1, user["step"] - 2)
        user["pos"] = 0
        await continue_step(msg.chat.id, msg.from_user.id)

async def start_timer(chat_id, user_id):
    user = user_states.get(user_id)
    step_data = next((s for s in steps if s["step"] == user["step"]), None)
    if not step_data:
        return
    try:
        duration = step_data["positions"][user["pos"]]["duration_min"] * 60
    except IndexError:
        return
    await asyncio.sleep(duration)
    user["pos"] += 1
    await continue_step(chat_id, user_id)

async def continue_step(chat_id, user_id):
    user = user_states.get(user_id)
    step_data = next((s for s in steps if s["step"] == user["step"]), None)
    if user["pos"] >= len(step_data["positions"]):
        await bot.send_message(chat_id, "Шаг завершён.", reply_markup=steps_keyboard())
        user_states.pop(user_id, None)
        return
    pos = step_data["positions"][user["pos"]]
    await bot.send_message(chat_id, f"{pos['name']} — {pos['duration_min']} мин", reply_markup=control_keyboard())
    await start_timer(chat_id, user_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
