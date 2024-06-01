import os, time
from aiogram import Router, F, Bot, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

from main import db, bot_main

router = Router()


from aiogram.filters.callback_data import CallbackData


class MyCallbackData(CallbackData, prefix="_"):
    param: str


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

        callback_data = MyCallbackData(param=button).pack()
        if builder_state:
            builder.row(InlineKeyboardButton(text=button_text, callback_data=callback_data))
        else:
            builder.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))

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


@router.callback_query(MyCallbackData.filter())
async def handle_callback(clb: types.CallbackQuery, callback_data: MyCallbackData):
    param = callback_data.param
    print(clb.message.chat.id)
    db.switch_buttons_locked(user_telegram_id=clb.message.chat.id, name=param)
    # await clb.message.answer(f"Button clicked with parameter: {param}")

    try:
        await profile_delete(clb)
    except Exception as ex:
        pass


@router.callback_query(F.data == 'button_name')
async def button_name(clb) -> None:
    db.switch_buttons_locked(user_telegram_id=clb.chat.id, name=button_name)
