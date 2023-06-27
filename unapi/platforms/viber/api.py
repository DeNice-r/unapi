import os

import requests
from os import environ


def send_message(chat_id, text: str):
    viber_token, min_api_version = environ['VIBER_TOKEN'], environ['VIBER_MIN_API_VERSION']

    send_message_url = 'https://chatapi.viber.com/pa/send_message'
    resp = requests.post(send_message_url,
                         json={
                             "receiver": chat_id,
                             "min_api_version": min_api_version,
                             "sender": {
                                 "name": "UnAPIBot"
                             },
                             "type": "text",
                             "text": text
                         },
                         headers={
                             'Content-Type': 'application/json',
                             'X-Viber-Auth-Token': viber_token
                         })
