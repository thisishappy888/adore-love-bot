from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import reply, inline
from utils.states import Form

import sqlite3

router = Router()

with sqlite3.connect("database.db") as db:
    cursor = db.cursor() 

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            bio TEXT,
            photo_file_id TEXT
        )
    ''')


async def get_random_profile(user_id):
    with sqlite3.connect('database.db') as db:
        cursor = db.cursor()

        cursor.execute('''SELECT * FROM profiles 
                       WHERE user_id != ? 
                       ORDER BY RANDOM() 
                       LIMIT 1''', (user_id,))
        profile = cursor.fetchone()  
        return profile 
        
@router.message(F.text.lower() == "смотреть анкеты")
async def view_profiles(message: Message, state: FSMContext):
    profile = await get_random_profile(message.from_user.id)

    if not profile:
        await message.answer("Анкет пока нет")
        return 

    response = (
        f"{profile[2]}, "
        f"{profile[3]} - "
        f"{profile[5]}"
    )
    
    await message.answer_photo(profile[6], caption=response, reply_markup=inline.main)


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (message.from_user.id,))
        profile = cursor.fetchone()

    if profile:
        await message.answer("Сколько тебе лет?", reply_markup=reply.get_age_keyboard(str(profile[3])))
    else:
        await message.answer("Сколько тебе лет?")
    


@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) < 100:
            await state.update_data(age=message.text)
            await state.set_state(Form.gender)
            await message.answer("Теперь определимся с полом", reply_markup=reply.gender_kb)
        else:
            await message.answer("Введите настоящий возраст")
    else:
        await message.answer("Введите число")


@router.message(Form.gender, F.text.casefold().in_(['парень', 'девушка']))
async def form_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(Form.bio)
    await message.answer("Расскажи о себе")


@router.message(Form.gender)
async def incorrect_form_gender(message: Message, state: FSMContext):
    await message.answer("Нажми на кнопку")


@router.message(Form.bio)
async def form_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    await state.set_state(Form.photo)
    await message.answer("Отправь фото")


@router.message(Form.photo, F.photo)
async def form_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()

    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO profiles(user_id, username, name, age, gender, bio, photo_file_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""", (message.from_user.id, 
                                          message.from_user.username,
                                          data['name'],
                                          data['age'],
                                          data['gender'],
                                          data['bio'],
                                          photo_file_id
                                          ))
        
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (message.from_user.id,))
        profile = cursor.fetchone()

    if profile:
        print(profile)
        print(type(profile))
        response = (
            f"{profile[2]}, "
            f"{profile[3]} - "
            f"{profile[5]}"
        )
        await message.answer_photo(profile[6], caption=response)
    else:
        await state.set_state(Form.name)
        await message.answer("Введите имя")
    await state.clear()

    print(data)

