import os
import asyncio
import logging

from aiogram import Dispatcher, Bot, F
from aiogram.types import BotCommand, ContentType
from dotenv import load_dotenv
from data.DataBase import DataBase

# Подключаем базу данных
db = DataBase('bot/data/database.db')

# Диспатчер
dp = Dispatcher()

load_dotenv()

bot_main = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))


from services import start, chat_join_request_handler, profile, order, my_subscribe, contacts


async def main_bot():
    dp.include_routers(
        start.router,
        chat_join_request_handler.router,
        profile.router,
        order.router,
        my_subscribe.router,
        contacts.router,
    )

    await bot_main.delete_my_commands()

    basic_commands = [
        BotCommand(command="/start", description="Начать")
    ]
    await bot_main.set_my_commands(commands=basic_commands)

    await dp.start_polling(bot_main, skip_updates=True)


async def main():
    await asyncio.gather(main_bot())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    db.create_tables()
    asyncio.run(main())