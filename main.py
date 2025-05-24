# coding: utf-8

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import os
import logging
from steps import steps

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@sunxstyle"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

user_states = {}

# Вспомогательные функции

def format_time(mins):
    mins = float(mins)
    whole = int(mins)
    sec = int((mins - whole) * 60)
    if whole and sec:
        return f"{whole} мин {sec} сек"
    elif whole:
        return f"{whole} мин"
    else:
        return f"{sec} сек"

def get_step_duration(step):
    total = sum([p['duration_min'] for p in step['positions']])
    h = int(total) // 60
    m = int(total) % 60
    if h and m:
        return f"{h} ч {m} мин"
    elif h:
        return f"{h} ч"
    else:
        return f"{m} мин"

def steps_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = [
        KeyboardButton(f"Шаг {s['step']} — {get_step_duration(s)}") for s in steps
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

def final_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(
        KeyboardButton("▶️ Продолжить"),
        KeyboardButton("📋 Вернуться к шагам"),
        KeyboardButton("↩️ Назад на 2 шага (если был перерыв)"),
        KeyboardButton("⛔ Завершить")
    )
    return kb

# Проверка подписки
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def check_sub_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Я подписан(а)", callback_data="check_sub"))
    return kb

# Приветствие
WELCOME = (
    "Привет, солнце! ☀️\n"
    "Ты в таймере по методу суперкомпенсации.\n"
    "Кожа адаптируется к солнцу постепенно — и загар становится ровным, глубоким и без ожогов.\n\n"
    "Начинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n\n"
    "Хочешь разобраться подробнее — жми /info. Там всё по делу."
)

INFO = (
    "ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n"
    "Он помогает коже адаптироваться к солнцу, снижая риск ожогов и пятен.\n\n"
    "Рекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое,\n"
    "и при отсутствии противопоказаний можно загорать без SPF.\n"
    "Так кожа включает свою естественную защиту: вырабатывается меланин и гормоны адаптации.\n\n"
    "С 11:00 до 17:00 — солнце более агрессивное. Если остаёшься на улице —\n"
    "надевай одежду, головной убор или используй SPF.\n\n"
    "Каждый новый день и после перерыва — возвращайся на 2 шага назад.\n"
    "Это нужно, чтобы кожа не перегружалась и постепенно усиливала защиту.\n\n"
    "Если есть вопросы — пиши: @sunxbeach_director"
)

# Команды
@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    if await is_subscribed(msg.from_user.id):
        await msg.answer(WELCOME, reply_markup=steps_keyboard())
    else:
        await msg.answer("Чтобы пользоваться ботом, нужно быть подписан(а) на канал @sunxstyle.",
                         reply_markup=check_sub_keyboard())

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def verify_sub(callback: types.CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await bot.send_message(callback.from_user.id, WELCOME, reply_markup=steps_keyboard())
    else:
        await callback.answer("Пока не вижу подписки...")

@dp.message_handler(commands=["info"])
async def info_cmd(msg: types.Message):
    await msg.answer(INFO)

@dp.message_handler(lambda m: m.text.startswith("Шаг "))
async def handle_step(msg: types.Message):
    try:
        step_num = int(msg.text.split()[1])
        step_data = next((s for s in steps if s["step"] == step_num), None)
        if not step_data:
            return await msg.answer("Шаг не найден")
        user_states[msg.from_user.id] = {"step": step_num, "pos": 0, "active": True}
        pos = step_data["positions"][0]
        await msg.answer(f"{pos['name']} — {format_time(pos['duration_min'])}", reply_markup=control_keyboard())
        await start_timer(msg.chat.id, msg.from_user.id)
    except:
        await msg.answer("Что-то пошло не так")

@dp.message_handler(lambda m: m.text in ["⏭️ Пропустить", "⛔ Завершить", "↩️ Назад на 2 шага (если был перерыв)", "📋 Вернуться к шагам"])
async def handle_controls(msg: types.Message):
    user = user_states.get(msg.from_user.id)
    if not user:
        return await msg.answer("Сначала выбери шаг.")
    if msg.text == "⏭️ Пропустить":
        user["pos"] += 1
        await continue_step(msg.chat.id, msg.from_user.id)
    elif msg.text == "⛔ Завершить":
        await msg.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=steps_keyboard())
        user_states.pop(msg.from_user.id, None)
    elif msg.text == "↩️ Назад на 2 шага (если был перерыв)":
        user["step"] = max(1, user["step"] - 2)
        user["pos"] = 0
        await continue_step(msg.chat.id, msg.from_user.id)
    elif msg.text == "📋 Вернуться к шагам":
        user_states.pop(msg.from_user.id, None)
        await msg.answer("Выбери шаг:", reply_markup=steps_keyboard())

async def start_timer(chat_id, user_id):
    user = user_states.get(user_id)
    if not user:
        return
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
        if user["step"] == 12:
            await bot.send_message(chat_id, "Ты завершил(а) все 12 шагов по методу суперкомпенсации!
Теперь можешь делать перерыв — или пройти цикл заново ☀️", reply_markup=final_keyboard())
        else:
            await bot.send_message(chat_id, "Шаг завершён!", reply_markup=final_keyboard())
        user_states.pop(user_id, None)
        return
    pos = step_data["positions"][user["pos"]]
    await bot.send_message(chat_id, f"{pos['name']} — {format_time(pos['duration_min'])}")
    await start_timer(chat_id, user_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
