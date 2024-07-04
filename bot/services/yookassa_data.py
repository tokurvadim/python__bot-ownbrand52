import os
from yookassa import Configuration, Payment
import uuid
from pprint import pprint
import logging
from time import sleep

SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
SECRET_KEY = os.getenv('YOOKASSA_API_TOKEN')

#Configuration.account_id = SHOP_ID
#Configuration.secret_key = SECRET_KEY


def create_payment(amount: int):
    Configuration.account_id = SHOP_ID
    Configuration.secret_key = SECRET_KEY

    id_key = str(uuid.uuid4())

    payment = Payment.create({
        'amount': {
            'value': amount,
            'currency': 'RUB'
        },
        'payment_method_data': {
            'type': 'bank_card'
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': 'https://t.me/ownbrand52_bot'
        },
        'capture': True,
        'description': 'Оплата подписки'
    }, id_key)

    return payment.confirmation.confirmation_url, payment.id

