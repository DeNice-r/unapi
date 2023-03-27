import requests
from os import environ


def send_message(chat_id, text: str):
    page_id, page_token, api_version = environ['FACEBOOK_PAGE_ID'], environ['FACEBOOK_PAGE_TOKEN'], environ['FACEBOOK_API_VERSION']
    send_message_url = f'https://graph.facebook.com/v{api_version}/{page_id}/messages?access_token={page_token}'
    resp = requests.post(send_message_url,
                         json={
                             "recipient": {
                                 "id": chat_id
                             },
                             "messaging_type": "RESPONSE",
                             "message": {
                                 "text": text
                             }
                         },
                         headers={
                             'Content-Type': 'application/json',
                         })
