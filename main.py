import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

import os

import keyboards

bot_token = os.environ.get("BOT_TOKEN")

bot = Bot(bot_token)
dp = Dispatcher()

@dp.message(CommandStart)
async def start(message: Message):
    await message.answer(f"Hello, {message.from_user.first_name}", reply_markup=keyboards.main_kb)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())