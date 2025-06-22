from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()
    bio = State()
    photo = State()

class PhotoChange(StatesGroup):
    photo = State()
    bio = State()