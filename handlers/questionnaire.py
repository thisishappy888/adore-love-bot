from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import reply, inline
from utils.states import Form, ChangeForm
from datetime import timedelta, datetime

import sqlite3

router = Router()


async def get_random_profile(user_id):
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()

        # Получаем список user_id, которые нельзя показывать (из-за таймаута)
        cursor.execute(
            """
            SELECT user_id FROM timeouts 
            WHERE timeout_until > datetime('now')
        """
        )
        timeout_ids = [row[0] for row in cursor.fetchall()]

        # Добавляем самого пользователя в список исключения
        excluded_ids = timeout_ids + [user_id]

        # Формируем SQL-запрос с исключениями
        placeholders = ",".join("?" for _ in excluded_ids)

        sql = f"""
            SELECT * FROM profiles 
            WHERE user_id NOT IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT 1
        """
        cursor.execute(sql, excluded_ids)
        profile = cursor.fetchone()

        return profile


@router.message(F.text.lower() == "смотреть анкеты")
async def view_profiles(message: Message, state: FSMContext):
    profile = await get_random_profile(message.from_user.id)

    if not profile:
        await message.answer("Анкет пока нет")
        return

    response = f"{profile[2]}, " f"{profile[3]} - " f"{profile[5]}"

    print(profile[0])
    await message.answer_photo(
        profile[6],
        caption=response,
        reply_markup=inline.get_profile_inline_kb(profile[0]),
    )


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id = ?", (message.from_user.id,)
        )
        profile = cursor.fetchone()

    if profile:
        await message.answer(
            "Сколько тебе лет?", reply_markup=reply.get_age_keyboard(str(profile[3]))
        )
    else:
        await message.answer("Сколько тебе лет?")


@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        if int(message.text) < 100:
            await state.update_data(age=message.text)
            await state.set_state(Form.gender)
            await message.answer(
                "Теперь определимся с полом", reply_markup=reply.gender_kb
            )
        else:
            await message.answer("Введите настоящий возраст")
    else:
        await message.answer("Введите число")


@router.message(Form.gender, F.text.casefold().in_(["парень", "девушка"]))
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

        cursor.execute(
            """
        INSERT OR REPLACE INTO profiles(user_id, username, name, age, gender, bio, photo_file_id) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                message.from_user.id,
                message.from_user.username,
                data["name"],
                data["age"],
                data["gender"],
                data["bio"],
                photo_file_id,
            ),
        )

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
        await message.answer_photo(profile[6], caption=response)
    else:
        await state.set_state(Form.name)
        await message.answer("Введите имя")
    await state.clear()

    print(data)


@router.message(ChangeForm.photo, F.photo)
async def form_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()

    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()

        cursor.execute(
            """UPDATE profiles SET photo_file_id = ?
                       WHERE user_id = ?""",
            (photo_file_id, message.from_user.id),
        )

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
        await message.answer_photo(profile[6], caption=response)

    await state.clear()

    await print(data)


@router.message(ChangeForm.bio)
async def form_photo(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    data = await state.get_data()

    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()

        cursor.execute(
            """UPDATE profiles SET bio = ?
                       WHERE user_id = ?""",
            (data["bio"], message.from_user.id),
        )

    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id = ?", (message.from_user.id,)
        )
        profile = cursor.fetchone()

    if profile:
        await print(profile)
        await print(type(profile))
        response = f"{profile[2]}, " f"{profile[3]} - " f"{profile[5]}"

        await message.answer("Так выглядит твоя анкета:")
        await message.answer_photo(profile[6], caption=response)

    await state.clear()

    print(data)


@router.callback_query(F.data.regexp(r"^(like|dislike):\d+$"))
async def handle_vote(callback: CallbackQuery):
    from_user_id = callback.from_user.id
    action, to_user_id_str = callback.data.split(":")
    to_user_id = int(to_user_id_str)
    link = f"tg://user?id={to_user_id}"

    from_username = callback.from_user.username or f"Без имени"

    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()

        cursor.execute("SELECT username FROM profiles WHERE user_id = ?", (to_user_id,))
        result = cursor.fetchone()
        if not result:
            await callback.answer("Ошибка. Пользователь не найден")
            return

        to_username = result[0] or "без_имени"

        if action == "like":
            cursor.execute(
                "INSERT OR IGNORE INTO likes(from_user, to_user) VALUES (?, ?)",
                (from_user_id, to_user_id),
            )
            cursor.execute(
                "SELECT * FROM likes WHERE from_user = ? AND to_user = ?",
                (to_user_id, from_user_id),
            )

            if cursor.fetchone():
                # Взаимный лайк — отправляем usernames
                await callback.message.answer("💘 У вас взаимный лайк!")

                await callback.bot.send_message(
                    chat_id=to_user_id,
                    text=f"🎉 У вас взаимный лайк с @{from_username}!",
                )
                await callback.bot.send_message(
                    chat_id=from_user_id,
                    text=f"🎉 У вас взаимный лайк с @{to_username}!",
                )
            else:
                # Односторонний лайк — отправляем анкету from_user_id -> to_user_id
                cursor.execute(
                    "SELECT name, age, bio, photo_file_id FROM profiles WHERE user_id = ?",
                    (from_user_id,),
                )
                sender_profile = cursor.fetchone()

                if sender_profile:
                    name, age, bio, photo_file_id = sender_profile
                    caption = f"{name}, {age} — {bio}"
                    await callback.message.answer("💘 У вас взаимный лайк!")
                    await callback.bot.send_photo(
                        chat_id=to_user_id,
                        photo=photo_file_id,
                        caption=caption,
                        reply_markup=inline.mutual_like_profile_inline_kb(from_user_id),
                    )
                else:
                    await callback.bot.send_message(
                        chat_id=to_user_id, text=f"❤️ Кто-то хочет с вами познакомиться!"
                    )

            await callback.answer("Лайк отправлен")

        elif action == "dislike":
            timeout_until = datetime.utcnow() + timedelta(minutes=1)
            cursor.execute(
                "INSERT OR REPLACE INTO timeouts(user_id, timeout_until) VALUES (?, ?)",
                (to_user_id, timeout_until),
            )
            cursor.execute(
                "INSERT INTO dislikes(from_user, to_user, timestamp) VALUES (?, ?, datetime('now'))",
                (from_user_id, to_user_id),
            )

            await callback.answer("Анкета скрыта на 1 минуту")

    await callback.message.delete()
