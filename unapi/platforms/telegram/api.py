import requests
from os import environ


def send_message(chat_id, text: str):
    token = environ['TELEGRAM_TOKEN']
    send_message_url = f'https://api.telegram.org/bot{token}/sendMessage'
    resp = requests.post(send_message_url,
                         json={
                             'chat_id': chat_id,
                             'text': text,
                         },
                         headers={
                             'Content-Type': 'application/json',
                         })
