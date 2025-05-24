# coding: utf-8

# ...
# (основной код из main.py до конца)

@dp.message_handler(lambda m: m.text)
async def debug_all_messages(msg: types.Message):
    print(f"DEBUG: text received: {msg.text}")
    await msg.answer("Ты нажал: " + msg.text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
