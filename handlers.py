# handlers.py
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Кнопки после завершения работы бота
end_session_kb = ReplyKeyboardMarkup(resize_keyboard=True)
end_session_kb.row(
    KeyboardButton("📋 Вернуться к шагам"),
    KeyboardButton("↩️ Назад на 2 шага")
)

async def end_session(message: types.Message):
    await message.answer("Сеанс завершён. Можешь вернуться позже и начать заново ☀️", reply_markup=end_session_kb)
