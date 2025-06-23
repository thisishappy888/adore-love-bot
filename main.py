import asyncio
from aiogram import Bot, Dispatcher

from handlers import commands, questionnaire, database
from config_reader import config


async def main():
    bot = Bot(config.bot_token.get_secret_value())
    dp = Dispatcher()

    dp.include_routers(commands.router, questionnaire.router, database.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
