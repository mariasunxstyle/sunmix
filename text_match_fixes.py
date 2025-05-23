# text_match_fixes.py
from aiogram import types

def normalize(text):
    return text.strip().replace("⏭️", "⏭️ ").replace("📋", "📋 ").replace("↩️", "↩️ ").replace("⛔", "⛔ ")

def match_button(text, target):
    return normalize(text) == normalize(target)

@dp.message_handler(lambda m: match_button(m.text, "⏭️ Пропустить"))
async def skip_handler(message: types.Message):
    await increment_index(message.from_user.id)
    await process_position(message)

@dp.message_handler(lambda m: match_button(m.text, "📋 Вернуться к шагам"))
async def back_to_steps(message: types.Message):
    await message.answer("Выбери шаг", reply_markup=steps_kb)

@dp.message_handler(lambda m: match_button(m.text, "↩️ Назад на 2 шага"))
async def back_two_steps(message: types.Message):
    state = user_states.get(message.from_user.id)
    if not state:
        await message.answer("Нет активного шага. Выбери шаг заново.", reply_markup=steps_kb)
        return
    new_step = max(1, state["step"] - 2)
    await step_handler(types.Message(
        message_id=message.message_id,
        date=message.date,
        chat=message.chat,
        text=f"Шаг {new_step}",
        from_user=message.from_user
    ))

@dp.message_handler(lambda m: match_button(m.text, "⛔ Завершить"))
async def finish_handler(message: types.Message):
    await reset_state(message.from_user.id)
    await end_session(message)
