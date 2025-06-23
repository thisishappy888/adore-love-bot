from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import reply
from utils.states import Form, ChangeForm

import sqlite3

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id = ?", (message.from_user.id,)
        )
        profile = cursor.fetchone()

    if profile:
        print(profile)
        print(type(profile))
        response = f"{profile[2]}, " f"{profile[3]} - " f"{profile[5]}"
        await message.answer("Так выглядит твоя анкета:")
        await message.answer_photo(
            profile[6], caption=response, reply_markup=reply.main
        )
    else:
        await state.set_state(Form.name)
        await message.answer("Введите имя")


@router.message(F.text.lower() == "заполнить анкету заново")
async def change_profile(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Введите имя")


@router.message(F.text.lower() == "изменить фото/видео")
async def change_profile(message: Message, state: FSMContext):
    await state.set_state(ChangeForm.photo)
    await message.answer("Отправьте фото")


@router.message(F.text.lower() == "изменить текст анкеты")
async def change_profile(message: Message, state: FSMContext):
    await state.set_state(ChangeForm.bio)
    await message.answer("Расскажи о себе")