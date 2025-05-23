# fix_back_to_steps.py
from aiogram import types
from keyboard import steps_kb

@dp.message_handler(lambda m: m.text.strip().startswith("📋"))
async def fixed_back_to_steps(message: types.Message):
    await message.answer("Выбери шаг", reply_markup=steps_kb)
