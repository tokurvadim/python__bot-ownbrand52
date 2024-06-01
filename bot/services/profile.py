import os, time
from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile
from aiogram.enums import ParseMode
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

from main import db, bot_main

router = Router()


@router.callback_query(F.data == 'profile_delete')
async def profile_delete(clb) -> None:
    buttons_data = db.get_buttons_data()
    pprint(buttons_data)

    buttons_locked = []
    if type(clb) is CallbackQuery:
        buttons_locked = db.get_buttons_locked(user_telegram_id=clb.message.chat.id)
    elif type(clb) is Message:
        buttons_locked = db.get_buttons_locked(user_telegram_id=clb.chat.id)

    pprint(buttons_locked)

    builder = InlineKeyboardBuilder()
    for index, button in enumerate(buttons_data):
        if index % 2 == 0:
            builder_state = True
        else:
            builder_state = False

        button_text = f'✅ {button}'
        if button in buttons_locked:
            button_text = f'❌ {button}'
        print(button)
        if builder_state:
            builder.row(InlineKeyboardButton(text=button_text, callback_data=f'{str(button)}'))
        else:
            builder.add(InlineKeyboardButton(text=button_text, callback_data=f'{str(button)}'))

    builder.row(InlineKeyboardButton(text='🔎 Взять кредит', callback_data='profile_search'))

    text = 'Нажмите для удаления тех контор, из которых вы уже брали займ'

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

        await previous_message.delete()


@router.callback_query(F.data == 'zaymer1')
async def zaymer1(clb) -> None:
    print('xd')
    db.switch_buttons_locked(user_telegram_id=clb.chat.id, name=button_name)



