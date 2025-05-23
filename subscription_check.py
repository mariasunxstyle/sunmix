# subscription_check.py
from aiogram import types

CHANNEL_USERNAME = "@sunxstyle"

async def is_user_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except Exception:
        return False

async def subscription_prompt(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Да, я подписан(а)", callback_data="check_subscription"))
    await message.answer(
        f"Чтобы продолжить, подпишись на канал {CHANNEL_USERNAME} и нажми кнопку ниже.",
        reply_markup=keyboard
    )
