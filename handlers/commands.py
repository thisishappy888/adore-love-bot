from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import reply
from utils.states import Form

import sqlite3

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    # await message.answer(f"Hello, {message.from_user.id}", reply_markup=inline.main)
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (message.from_user.id,))
        profile = cursor.fetchone()

    if profile:
        print(profile)
        print(type(profile))
        response = (
            f"Имя: {profile[2]}\n"
            f"Возраст: {profile[3]}\n"
            f"Пол: {profile[4]}\n"
            f"О себе: {profile[5]}\n"
        )
        await message.answer_photo(profile[6], caption=response, reply_markup=reply.main)
    else:
        await state.set_state(Form.name)
        await message.answer("Введите имя")

@router.message(F.text.lower() == "заполнить анкету заново")
async def change_profile(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Введите имя")
    