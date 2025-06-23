from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import sqlite3

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Смотреть анкеты"),
            KeyboardButton(text="Заполнить анкету заново"),
        ],
        [
            KeyboardButton(text="Изменить фото/видео"),
            KeyboardButton(text="Изменить текст анкеты"),
        ],
    ],
    one_time_keyboard=True,
    resize_keyboard=True,
)

gender_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="парень"), KeyboardButton(text="девушка")]],
    one_time_keyboard=True,
    resize_keyboard=True,
)


def get_age_keyboard(text: str):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=text))
    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)
