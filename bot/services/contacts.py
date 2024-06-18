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

@router.callback_query(F.data == 'contacts')
async def contacts(clb: CallbackQuery):
    builder = InlineKeyboardBuilder()

    default_text: str = f'✅ При возникновении вопросов по боту или каналу, а также по вопросам сотрудничества обращайтесь в личные сообщения владельцу группы @ElenaC666'

    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='start'))

    await clb.message.delete()
    
    await clb.message.answer(
            text=default_text,
            reply_markup=builder.as_markup(),
    )