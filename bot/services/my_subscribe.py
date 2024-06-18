import os, time
from aiogram import Router, F, Bot, types
from aiogram.filters import Command, callback_data
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, BotCommand, LabeledPrice, PreCheckoutQuery, ContentType
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile
from aiogram.types.web_app_info import WebAppInfo
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import create_chat_invite_link, answer_pre_checkout_query, SendInvoice
from pprint import pprint
from dotenv import load_dotenv
import datetime
load_dotenv()

from main import db, bot_main, dp

router = Router()

@router.callback_query(F.data == 'my_subscribe')
async def my_subscribe(clb: CallbackQuery):
    user_subscribe: int = db.get_user_subscribe(user_telegram_id=clb.message.chat.id)[0]

    builder = InlineKeyboardBuilder()

    default_text: str = f'Подписка найдена✅\n\nКоличество дней подписки: {user_subscribe}'
    text: str = ''
    if user_subscribe == 1:
        attention_text: str = '\n\n❗Ваша подписка закончится уже завтра! Рекомендуем ее продлить во избежание исключения из закрытого канала!'
        text = default_text + attention_text
    else:
        text = default_text

    builder.row(InlineKeyboardButton(text='🔗 Продлить подписку', callback_data='order_choice'))
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='start'))

    await clb.message.delete()
    
    await clb.message.answer(
            text=text,
            reply_markup=builder.as_markup(),
    )