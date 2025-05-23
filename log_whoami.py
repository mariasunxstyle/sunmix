from aiogram import types

def log_whoami(message: types.Message):
    print(f"USER ID: {message.from_user.id} | name: {message.from_user.full_name}")