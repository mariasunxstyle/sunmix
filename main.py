# main.py
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
import asyncio
import os
from steps import steps
from utils import format_duration

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@sunxstyle"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
user_states = {}

# Кнопки
def generate_steps_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for step in steps:
        duration = sum(x[1] for x in step['positions'])
        label = f"Шаг {step['step']} ({format_duration(duration)})"
        kb.insert(KeyboardButton(label))
    kb.add(KeyboardButton("ℹ️ Инфо"))
    return kb

control_kb = ReplyKeyboardMarkup(resize_keyboard=True)
control_kb.add(
    KeyboardButton("⏭️ Пропустить"),
    KeyboardButton("⛔ Завершить"),
    KeyboardButton("↩️ Назад на 2 шага"),
    KeyboardButton("📋 Вернуться к шагам")
)

done_kb = ReplyKeyboardMarkup(resize_keyboard=True)
done_kb.add(
    KeyboardButton("▶️ Продолжить"),
    KeyboardButton("📋 Вернуться к шагам"),
    KeyboardButton("↩️ Назад на 2 шага"),
    KeyboardButton("⛔ Завершить")
)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(
        "Привет, солнце! ☀️\nТы в таймере по методу суперкомпенсации.\nНачни с шага 1.",
        reply_markup=generate_steps_kb()
    )

@dp.message_handler(lambda m: m.text == "ℹ️ Инфо")
async def info_handler(message: types.Message):
    await message.answer(
        "Метод суперкомпенсации — безопасный путь к загару без ожогов.\n"
        "Загорай утром до 11 и вечером после 17 без SPF, в остальное время — под защитой."
    )

@dp.message_handler(lambda m: m.text.startswith("Шаг "))
async def step_handler(message: types.Message):
    try:
        step_number = int(message.text.split()[1])
        step = next(s for s in steps if s['step'] == step_number)
        user_states[message.from_user.id] = {"step": step_number, "positions": step["positions"], "index": 0}
        await run_step(message)
    except:
        await message.answer("Не могу начать шаг")

async def run_step(message):
    state = user_states.get(message.from_user.id)
    if not state:
        return
    index = state["index"]
    if index >= len(state["positions"]):
        await message.answer("Шаг завершён ☀️", reply_markup=done_kb)
        return
    pos, dur = state["positions"][index]
    await message.answer(f"{pos} — {format_duration(dur)}", reply_markup=control_kb)
    await asyncio.sleep(int(dur * 60))
    state["index"] += 1
    await run_step(message)

@dp.message_handler(lambda m: m.text == "⏭️ Пропустить")
async def skip_position(message: types.Message):
    if message.from_user.id in user_states:
        user_states[message.from_user.id]["index"] += 1
        await run_step(message)

@dp.message_handler(lambda m: m.text == "↩️ Назад на 2 шага")
async def back_two_steps(message: types.Message):
    current = user_states.get(message.from_user.id)
    if not current:
        return await message.answer("Сначала выбери шаг")
    new_step = max(1, current["step"] - 2)
    await step_handler(types.Message(
        message_id=message.message_id,
        date=message.date,
        chat=message.chat,
        text=f"Шаг {new_step}",
        from_user=message.from_user
    ))

@dp.message_handler(lambda m: m.text == "📋 Вернуться к шагам")
async def back_to_menu(message: types.Message):
    await message.answer("Выбери шаг", reply_markup=generate_steps_kb())

@dp.message_handler(lambda m: m.text == "⛔ Завершить")
async def end_session(message: types.Message):
    user_states.pop(message.from_user.id, None)
    await message.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=generate_steps_kb())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
