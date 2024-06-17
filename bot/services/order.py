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
        builder.row(InlineKeyboardButton(text=f'{price[0]} дней: {price[1]} RUB', callback_data=callback))
    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='start'))

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


@router.callback_query(MyCallbackData.filter())
async def order(clb: CallbackQuery, bot: Bot, callback_data: MyCallbackData) -> SendInvoice:
    await bot.send_invoice(
        chat_id=clb.message.chat.id,
        title='''Покупка подписка на канал "Личный бренд"''',
        description='Оплата подписки',
        payload='Payload through Telegram Bot',
        provider_token=provider_token,
        currency='RUB',
        prices=[
            LabeledPrice(
                label=f'{callback_data.days} дней',
                amount=callback_data.price * 100
            )
        ],
        protect_content=True,
        allow_sending_without_reply=True,
        reply_markup=None,
    )


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    print(f'Запрос на платеж от пользователя {pre_checkout_query.from_user.id} на сумму {pre_checkout_query.total_amount}')

    prices = db.get_price_data()
    subscribe: int

    for price in prices.items():
        if price[1] == pre_checkout_query.total_amount // 100:
            subscribe = price[0]

    db.update_user_subscribe(subscribe=subscribe, user_telegram_id=pre_checkout_query.from_user.id)

    await pre_checkout_query.answer(ok=True)


@router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successfull_payment(message: Message, bot: Bot):
    print(f'Платеж от пользователя {message.chat.id} прошел успешно')

    user_status = db.get_user_status(user_telegram_id=message.chat.id)[0]

    if user_status:
        text = 'Поздравляем вас с продлением подписки! Теперь вы можете дольше составлять свой личный бренд!'

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='⬅️ В начало', callback_data='start'))

        await message.delete()

        await message.answer(text=text, reply_markup=builder.as_markup())
    else:
        db.update_user_status(user_telegram_id=message.chat.id, status=1)

        date = datetime.datetime.now() + datetime.timedelta(days=1)
        link = await bot.create_chat_invite_link(chat_id=channel_id, member_limit=1, creates_join_request=False, expire_date=date, name='own_brand_52')
        text = f'Поздравляем со вступлением в лучший канал по составлению личного бренда\! Ссылка на вход в группу уже сформирована: {link.invite_link} (ВНИМАНИЕ: ссылка действует только 1 раз и истекает в течение 24 часов!)'

        await message.delete()

        await message.answer(text=text)
    