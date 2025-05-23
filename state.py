# state.py
from aiogram.types import Message

user_states = {}

async def reset_state(user_id):
    user_states.pop(user_id, None)

async def update_state(user_id, step, positions):
    user_states[user_id] = {"step": step, "positions": positions, "index": 0}

async def get_current_position(user_id):
    state = user_states.get(user_id)
    if not state:
        return None, None
    index = state["index"]
    if index >= len(state["positions"]):
        return None, None
    return state["positions"][index], index

async def increment_index(user_id):
    if user_id in user_states:
        user_states[user_id]["index"] += 1
