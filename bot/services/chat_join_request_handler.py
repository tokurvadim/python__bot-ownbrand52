import os
import re
import time
from string import punctuation
from pprint import pprint
from datetime import datetime

from aiogram import Bot, Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.enums import ParseMode


from main import db, bot_main

router = Router()


async def send_user_message(user_id, text):
    try:
        await bot_main.send_message(chat_id=user_id, text=text)
    except Exception as ex:
        print('Не удалось отправить сообщение:')
        print(ex)


@router.chat_join_request()
async def chat_join_handler(clb):
    pprint(clb)

    db.add_user(user_telegram_id=clb.from_user.id)
    db.set_group_joined_true(user_telegram_id=clb.from_user.id)

    await clb.approve()
