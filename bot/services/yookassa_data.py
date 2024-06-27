import os
from yookassa import Configuration, Payment
import uuid

SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
SECRET_KEY = os.getenv('YOOKASSA_API_TOKEN')

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

def create_payment(amount: int, user_id: int):
    id_key = str(uuid.uuid4)
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
        'metadata': {
            'chat_id': user_id
        },
        'description': 'Оплата подписки'
    }, id_key)

    return payment.confirmation.confirmation_url, payment.id

