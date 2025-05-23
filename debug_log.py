# debug_log.py
from aiogram import types

def log_action(action: str, message: types.Message):
    print(f"DEBUG | {action} | user_id: {message.from_user.id} | text: {message.text}")
