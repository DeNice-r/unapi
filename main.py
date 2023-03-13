import asyncio
import random
import hmac
import hashlib
import logging
import json

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

import telegram
import viber
import facebook
import webhooks

from os import environ

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app = FastAPI()

telegram_verification_token = environ['TELEGRAM_VERIFICATION_TOKEN']
viber_token = environ['VIBER_TOKEN']
facebook_verification_token = environ['FACEBOOK_VERIFICATION_TOKEN']
facebook_app_secret = environ['FACEBOOK_APP_SECRET']


class Message:
    text: str
    chat_id: str

    def __init__(self, chat_id: str, text: str):
        self.chat_id = chat_id
        self.text = text

    @classmethod
    def from_telegram(cls, telegram_json):
        return cls(
            str(telegram_json['message']['chat']['id']),
            telegram_json['message']['text'],
        )

    @classmethod
    def from_viber(cls, viber_json):
        return cls(
            viber_json['sender']['id'],
            viber_json['message']['text'],
        )

    @classmethod
    def from_facebook(cls, facebook_json):
        return cls(
            facebook_json['entry'][0]['messaging'][0]['sender']['id'],
            facebook_json['entry'][0]['messaging'][0]['message']['text'],
        )


@app.get("/")
async def index():
    r = random.Random()
    return (
        f"I'm ok {r.uniform(0, 1000)}",
        'https://unapi.pp.ua/init'
        )


@app.get("/init")
async def webhook_init():
    await webhooks.init()
    return f"I'm ok"


@app.post("/webhook/telegram")
async def telegram_callback(request: Request):
    body = await request.json()
    verification_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if telegram_verification_token == verification_token and body['message']:
        message = Message.from_telegram(body)
        telegram.send_message(message.chat_id, message.text)
        return "OK"
    return HTTPException(status_code=404, detail="Not found")


class ViberBody(BaseModel):
    event: str
    message: dict[str, str] | None


@app.post("/webhook/viber")
async def viber_callback(request: Request, viber_body: ViberBody):
    raw_body, body = await asyncio.gather(request.body(), request.json())
    signature_hash = request.headers.get('X-Viber-Content-Signature')
    if signature_hash:
        h = hmac.new(viber_token.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
        if signature_hash == h and viber_body.event == 'message':
            message = Message.from_viber(body)
            viber.send_message(message.chat_id, message.text)
            return "OK"
    return HTTPException(status_code=404, detail="Not found")


class FbBody(BaseModel):
    object: str
    entry: list


@app.get("/webhook/facebook")
async def facebook_subscribe(mode: str = Query(None, alias="hub.mode"),
                             verify_token: str = Query(None, alias="hub.verify_token"),
                             challenge: int = Query(None, alias="hub.challenge")):
    if verify_token == facebook_verification_token and mode == 'subscribe':
        return challenge
    raise HTTPException(status_code=403, detail="Invalid key")


@app.post("/webhook/facebook")
async def facebook_callback(request: Request, fb_body: FbBody):
    raw_body, body = await asyncio.gather(request.body(), request.json())
    signature_hash = request.headers.get('X-Hub-Signature-256').split('=')[1]
    h = hmac.new(facebook_app_secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    if signature_hash == h and fb_body.object == 'page':
        message = Message.from_facebook(body)
        facebook.send_message(message.chat_id, message.text)
        return "EVENT_RECEIVED"
    return HTTPException(status_code=404, detail="Not found")
