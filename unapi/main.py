import asyncio
import random
import hmac
import hashlib
import logging

from fastapi import FastAPI, HTTPException, Query, Request

from util import webhook_urljoin

from event import EventFactory

from unapi.platforms import facebook, viber, telegram  # to be removed
import webhooks

from os import environ

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
app = FastAPI()

webhook_path = environ["WEBHOOK_PATH"]

telegram_verification_token = environ["TELEGRAM_VERIFICATION_TOKEN"]
viber_token = environ["VIBER_TOKEN"]
facebook_verification_token = environ["FACEBOOK_VERIFICATION_TOKEN"]
facebook_app_secret = environ["FACEBOOK_APP_SECRET"]


@app.get("/")
async def index():
    r = random.Random()
    return (
        f"I'm ok {r.uniform(0, 1000)}",
        "https://unapi.pp.ua/init",
        webhook_urljoin(webhook_path, "telegram")
        )


@app.get("/init")
async def webhook_init():
    await webhooks.init()
    return f"I'm ok"


@app.post(webhook_urljoin(webhook_path, "telegram"))
async def telegram_callback(request: Request):
    body = await request.json()
    verification_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if telegram_verification_token == verification_token and body["message"]:
        # The request is valid therefore calling user callback

        message = EventFactory.create_event(body)
        message.send_message(message.text)
        return "OK"
    return HTTPException(status_code=404, detail="Not found")


@app.post(webhook_urljoin(webhook_path, "viber"))
async def viber_callback(request: Request):
    raw_body, body = await asyncio.gather(request.body(), request.json())
    signature_hash = request.headers.get("X-Viber-Content-Signature")
    if signature_hash:
        h = hmac.new(viber_token.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
        if signature_hash == h and body["event"] == "message":
            # The request is valid therefore calling user callback

            message = EventFactory.create_event(body)
            message.send_message(message.text)
            return "OK"
    return HTTPException(status_code=404, detail="Not found")


@app.get("/webhook/facebook")
async def facebook_subscribe(mode: str = Query(None, alias="hub.mode"),
                             verify_token: str = Query(None, alias="hub.verify_token"),
                             challenge: int = Query(None, alias="hub.challenge")):
    if verify_token == facebook_verification_token and mode == "subscribe":
        return challenge
    raise HTTPException(status_code=403, detail="Invalid key")


@app.post(webhook_urljoin(webhook_path, "facebook"))
async def facebook_callback(request: Request):
    raw_body, body = await asyncio.gather(request.body(), request.json())
    signature_hash = request.headers.get("X-Hub-Signature-256").split("=")[1]
    h = hmac.new(facebook_app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    if signature_hash == h and body["object"] == "page":
        # The request is valid therefore calling user callback

        message = EventFactory.create_event(body)
        message.send_message(message.text)
        return "EVENT_RECEIVED"
    return HTTPException(status_code=404, detail="Not found")
