import os, time
from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from main import db, bot_main
from dotenv import load_dotenv
load_dotenv()

from .profile import profile_delete
router = Router()


@router.message(Command("start"))
async def start(clb) -> None:
    if type(clb) is Message:
        if str(clb.chat.id)[0] == '-':
            print('С группы сообщение')
            return

    db.add_user(user_telegram_id=clb.chat.id)
    if db.get_user_group_joined(user_telegram_id=clb.chat.id):
        await profile_delete(clb)
        return

    previous_message = clb

    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🔗 Подписаться', url=os.getenv("TELEGRAM_GROUP_URL")))
    builder.row(InlineKeyboardButton(text='✅ Проверить подписку', callback_data='check_subscribe'))

    clb: Message = clb

    sent_message = await clb.answer(
        text='👋 Приветствую\!\n'
             '*Подпишитесь* на наш *официальный* канал для того, чтобы начать пользоваться *ботом*\!',
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    db.set_last_bot_message_id(user_telegram_id=clb.chat.id, last_bot_message_id=sent_message.message_id)
    await previous_message.delete()


@router.callback_query(F.data == 'check_subscribe')
async def check_subscribe(clb) -> None:
    if not db.get_user_group_joined(user_telegram_id=clb.message.chat.id):
        await bot_main.answer_callback_query(callback_query_id=clb.id, text='Вы не подписались', show_alert=True)
        return

    await profile_delete(clb)
