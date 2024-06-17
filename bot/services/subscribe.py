import os, time
from aiogram import Router, F, Bot, types
from aiogram.filters import Command, callback_data
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, BotCommand, LabeledPrice, PreCheckoutQuery, ContentType
#from aiogram.filters import 
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

provider_token = os.getenv('TELEGRAM_PAYMENT_TOKEN')
channel_id = os.getenv('TELEGRAM_CHANNEL_ID')

class MyCallbackData(callback_data.CallbackData, prefix="_"):
    days: int
    price: int


@router.callback_query(F.data == 'order_choice')
async def order_choice(clb: CallbackQuery, bot: Bot) -> SendInvoice:
    text = 'Выберите желаемый вариант подписки:'

    builder = InlineKeyboardBuilder()
    prices = db.get_table_price()

    for price in prices:
        callback = MyCallbackData(days=price[0], price=price[1]).pack()
        builder.row(InlineKeyboardButton(text=f'{price[0]} дней: {price[1]} RUB'), callback_data=callback)

    if type(clb) is CallbackQuery:
        message = clb.bot.edit_message_reply_markup
        await message(
            chat_id=clb.message.chat.id,
            message_id=clb.message.message_id,
            reply_markup=builder.as_markup()
        )

        await clb.message.edit_text(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.MARKDOWN_V2
        )
    elif type(clb) is Message:
        previous_message = clb

        clb: Message = clb

        await clb.answer(
            text=text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.MARKDOWN_V2
        )
