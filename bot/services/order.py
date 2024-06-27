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
import yookassa
load_dotenv()

from main import db, bot_main, dp
from services.yookassa_data import create_payment

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
        builder.row(InlineKeyboardButton(text=f'{price[0]} дней: {price[1]} RUB 💰', callback_data=callback))

    builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='start'))

    await clb.bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)

    await clb.message.answer(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.MARKDOWN_V2
    )


@router.callback_query(MyCallbackData.filter())
async def order(clb: CallbackQuery, bot: Bot, callback_data: MyCallbackData):
    try:
        payment_url, payment_id = create_payment(amount=callback_data.price, user_id=clb.message.chat.id)

        payment = yookassa.Payment.find_one(payment_id=payment_id)

        print(f'Запрос на платеж от пользователя {clb.message.chat.id} на сумму {payment.amount.value} RUB')

        text: str = '🔥 Ваша ссылка на оплату готова\! Вы в одном шаге от получения лучших советов по продвижению личного бренда\!\n❗*ВНИМАНИЕ:* после проведения оплаты *ОБЯЗАТЕЛЬНО* нажмите кнопку *✅ Проверить подписку* для регистрации оплаты внутри бота\!"'

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='💜 Оплатить', url=payment_url))
        builder.row(InlineKeyboardButton(text='✅ Проверить подписку', callback_data=f'check_{payment_id}_{int(payment.amount.value)}'))

        await clb.bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)

        await clb.message.answer(text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception:
        print(f'Платеж от пользователя {clb.message.chat.id} не прошел')

        text = '🤕 Кажется, что-то пошло не так... Попробуйте провести оплату позже.'

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='start'))

        await clb.bot.delete_message(chat_id=clb.message.chat.id, message_id=clb.message.message_id)
        await clb.message.answer(text=text, reply_markup=builder.as_markup())





@router.callback_query(lambda c: 'check' in c.data)
async def check_payment(clb: CallbackQuery):
    result = check(clb.data.split('_')[-2])
    payment_amount = int(clb.data.split('_')[-1])

    if result:
        print(f'Платеж от пользователя {clb.message.chat.id} прошел успешно')

        prices = db.get_price_data()
        subscribe: int

        for price in prices.items():
            if price[1] == payment_amount:
                subscribe = price[0]

        db.update_user_subscribe(subscribe=subscribe, user_telegram_id=clb.message.chat.id)

        user_status = db.get_user_status(user_telegram_id=clb.message.chat.id)[0]

        if user_status == 1:
            text = '🤩*Поздравляем вас с продлением подписки\!*\nТеперь вы можете еще дольше составлять свой личный бренд\!'

            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text='⬅️ В начало', callback_data='start'))

            await clb.message.delete()
            await clb.message.answer(text=text, reply_markup=builder.as_markup(), parse_mode=ParseMode.MARKDOWN_V2)

        else:
            db.update_user_status(user_telegram_id=clb.message.chat.id, status=1)

            date = datetime.datetime.now() + datetime.timedelta(days=1)
            link = await clb.bot.create_chat_invite_link(chat_id=channel_id, member_limit=1, creates_join_request=False, expire_date=date, name='own_brand_52')
            text = f'🥳 Поздравляем со вступлением в лучший канал по составлению личного бренда! Ссылка на вход в группу уже сформирована: {link.invite_link}\n❗*ВНИМАНИЕ:* ссылка действует только 1 раз и истекает в течение 24 часов!'

            await clb.message.delete()
            await clb.message.answer(text=text)

    else:
        print(f'Платеж от пользователя {clb.message.chat.id} не прошел')

        text = '🤕 Кажется, что-то пошло не так... Попробуйте провести оплату позже.'

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='⬅️ Назад', callback_data='start'))

        await clb.message.delete()
        await clb.message.answer(text=text, reply_markup=builder.as_markup())
    


def check(payment_id):
    payment = yookassa.Payment.find_one(payment_id=payment_id)
    return payment.status == 'succeeded'