import os, time
from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from main import db, bot_main
from dotenv import load_dotenv
load_dotenv()

router = Router()


@router.message(Command("start"))
async def start(clb) -> None:
    if type(clb) is Message:
        if str(clb.chat.id)[0] == '-':
            print('С группы сообщение')
            return

    db.add_user(user_telegram_id=clb.chat.id)

    builder = InlineKeyboardBuilder()
    
    text: str

    if db.get_user_status(user_telegram_id=clb.chat.id)[0] == 1:
        text = '👋 Приветствуем вас в боте канала *Личный бренд*\! Здесь вы можете управлять своей подпиской\.'
        builder.row(InlineKeyboardButton(text='🔗 Продлить подписку', callback_data='order_choice'))
        builder.row(InlineKeyboardButton(text='✅ Моя подписка', callback_data='my_subscribe'))
        builder.row(InlineKeyboardButton(text='❗ Контакты', callback_data='contacts'))
    else:
        text='🤖 Привет\!\nЯ ваш персональный бот, помогающий развивать личный бренд\.\nЧтобы воспользоваться всеми нашими функциями, пожалуйста, оформите подписку на закрытый канал\.'
        builder.row(InlineKeyboardButton(text='🔗 Оформить подписку', callback_data='order_choice'))


    await clb.delete()
    
    await clb.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@router.callback_query(F.data == 'start')
async def start(clb: CallbackQuery):
    builder = InlineKeyboardBuilder()
    
    text: str

    if db.get_user_status(user_telegram_id=clb.message.chat.id)[0] == 1:
        text = '👋 Приветствуем вас в боте канала *Личный бренд*\! Здесь вы можете управлять своей подпиской\.'
        builder.row(InlineKeyboardButton(text='🔗 Продлить подписку', callback_data='order_choice'))
        builder.row(InlineKeyboardButton(text='✅ Моя подписка', callback_data='my_subscribe'))
        builder.row(InlineKeyboardButton(text='❗ Контакты', callback_data='contacts'))
    else:
        text='🤖 Привет\!\nЯ ваш персональный бот, помогающий развивать личный бренд\.\nЧтобы воспользоваться всеми нашими функциями, пожалуйста, оформите подписку на закрытый канал\.'
        builder.row(InlineKeyboardButton(text='🔗 Оформить подписку', callback_data='order_choice'))


    await clb.message.delete()
    
    await clb.message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.MARKDOWN_V2
    )
