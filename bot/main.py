import os
import asyncio
import logging
import schedule

from aiogram import Dispatcher, Bot, F
from aiogram.types import BotCommand, ContentType, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import datetime

from data.DataBase import DataBase

# Подключаем базу данных
db = DataBase('bot/data/database.db')

# Диспатчер
dp = Dispatcher()

load_dotenv()

bot_main = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))


from services import start, order, my_subscribe, contacts


async def main_bot():
    dp.include_routers(
        start.router,
        order.router,
        my_subscribe.router,
        contacts.router,
    )

    await bot_main.delete_my_commands()

    basic_commands = [
        BotCommand(command="/start", description="Начать")
    ]

    users = db.get_users()
    schedule.every().day.at("09:00").do(check_subscribe, users=users, bot=bot_main)

    await bot_main.set_my_commands(commands=basic_commands)

    await dp.start_polling(bot_main, skip_updates=True)


async def waiter():
    while True:
        await asyncio.sleep(15)
        schedule.run_pending()


def check_subscribe(users: list, bot: Bot):
    for user in users:
        try:
            user_status = user[3]
            user_id = user[0]

            db.reduce_user_subscribe(user_telegram_id=user_id)
            user_subscribe = db.get_user_subscribe(user_telegram_id=user_id)[0]

            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text='🔗 Продлить подписку', callback_data='order_choice'))

            if user_subscribe == 1:
                text = '❗*ВНИМАНИЕ!* Напоминаем, что ваша подписка на канал *Личный бренд* закончится уже завтра\!\nЧтобы не потерять доступ, рекоменудем продлить подписку\.'
                asyncio.run_coroutine_threadsafe(coro=bot.send_message(chat_id=user_id, text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN_V2), loop=asyncio.get_event_loop())

            elif user_subscribe == 0 and user_status:
                db.update_user_status(user_telegram_id=user_id, status=0)

                asyncio.run_coroutine_threadsafe(coro=bot.ban_chat_member(chat_id=os.getenv('TELEGRAM_CHANNEL_ID'), user_id=user[0], until_date=datetime.datetime.now() + datetime.timedelta(seconds=60)), loop=asyncio.get_event_loop())

                text = '❗Уведомляем вас, что подписка на канал *Личный бренд* подошла к концу, вы были автоматически исключены из канала\. Чтобы вернуть доступ, продлите подписку\.\n*ВНИМАНИЕ*: после получения этого сообщения подождите РОВНО 60 секунд, прежде чем продлить подписку\.'

                asyncio.run_coroutine_threadsafe(coro=bot.send_message(chat_id=user_id, text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN_V2), loop=asyncio.get_event_loop())

            else:
                pass

        except TelegramForbiddenError:
            db.delete_user(user_telegram_id=user_id)



async def main():
    await asyncio.gather(main_bot(), waiter())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    db.create_tables()
    asyncio.run(main())