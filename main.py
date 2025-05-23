# sunxstyle_bot: бот для загара по методу суперкомпенсации

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
import asyncio
import os
from steps import steps
from subscription_check import is_user_subscribed, subscription_prompt
from handlers import end_session, end_session_kb

API_TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@sunxstyle"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Кнопка старта
start_kb = ReplyKeyboardMarkup(resize_keyboard=True)
start_kb.add(KeyboardButton("Старт ☀️"))

# Кнопки шагов
steps_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
for step in steps:
    label = f"Шаг {step['step']}"
    steps_kb.insert(KeyboardButton(label))
steps_kb.add(KeyboardButton("ℹ️ Инфо"))

# Кнопки управления во время шага
control_kb = ReplyKeyboardMarkup(resize_keyboard=True)
control_kb.row(KeyboardButton("⏭️ Пропустить"))
control_kb.row(KeyboardButton("⛔ Завершить"))
control_kb.row(KeyboardButton("↩️ Назад на 2 шага"))
control_kb.row(KeyboardButton("📋 Вернуться к шагам"))

# Кнопки после завершения шага
done_kb = ReplyKeyboardMarkup(resize_keyboard=True)
done_kb.row(KeyboardButton("▶️ Продолжить"), KeyboardButton("📋 Вернуться к шагам"), KeyboardButton("↩️ Назад на 2 шага"), KeyboardButton("⛔ Завершить"))

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    if not await is_user_subscribed(bot, message.from_user.id):
        await subscription_prompt(message)
        return
    await message.answer("Привет, солнце! ☀️\nТы в таймере по методу суперкомпенсации.\n\nНачинай с шага 1. Даже если уже немного загорел(а), важно пройти путь с начала.\nКаждый новый день и после перерыва — возвращайся на 2 шага назад.\n\nХочешь разобраться подробнее — жми ℹ️ Инфо.", reply_markup=steps_kb)

@dp.callback_query_handler(lambda c: c.data == 'check_subscription')
async def check_subscription(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if await is_user_subscribed(bot, user_id):
        await bot.send_message(user_id, "Спасибо за подписку! ☀️", reply_markup=steps_kb)
    else:
        await bot.send_message(user_id, "Ты ещё не подписан(а). Пожалуйста, подпишись и нажми снова.")

@dp.message_handler(lambda m: m.text == "ℹ️ Инфо")
async def info_handler(message: types.Message):
    await message.answer("ℹ️ Метод суперкомпенсации — это безопасный, пошаговый подход к загару.\n\nРекомендуем загорать с 7:00 до 11:00 и после 17:00 — в это время солнце мягкое.\nС 11:00 до 17:00 — солнце агрессивное, надевай одежду или используй SPF.\n\nКаждый новый день и после перерыва — возвращайся на 2 шага назад.\n\nЕсли есть вопросы — пиши: @sunxbeach_director")

@dp.message_handler(lambda m: m.text.startswith("Шаг "))
async def step_handler(message: types.Message):
    if not await is_user_subscribed(bot, message.from_user.id):
        await subscription_prompt(message)
        return

    step_num = int(message.text.replace("Шаг ", ""))
    step = next((s for s in steps if s['step'] == step_num), None)
    if not step:
        await message.answer("Шаг не найден.")
        return
    for position, duration in step['positions']:
        await message.answer(f"{position} — {duration} мин", reply_markup=control_kb)
        await asyncio.sleep(duration * 60)
    await message.answer("Шаг завершён. ☀️\nМожешь продолжить или вернуться.", reply_markup=done_kb)

@dp.message_handler(lambda m: m.text == "⛔ Завершить")
async def finish_handler(message: types.Message):
    await end_session(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
