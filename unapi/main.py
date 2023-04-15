import random
import logging

from fastapi import FastAPI, HTTPException, Query, Request

from unapi.event import EventFactory
from unapi import platforms

from unapi.webhooks import init as webhooks_init

from os import environ

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
app = FastAPI()

webhook_path = environ["WEBHOOK_PATH"]


@app.get("/")
async def index():
    r = random.Random()
    return (
        f"I'm ok {r.uniform(0, 1000)}",
        "https://unapi.pp.ua/init",
        )


@app.get("/init")
async def webhook_init():
    await webhooks_init()
    return f"I'm ok"


@app.post(webhook_path)
async def webhook_callback(request: Request):
    message = None
    try:
        message = await EventFactory.create_event(request)
    except ValueError as e:
        return HTTPException(status_code=400, detail=str(e))
    message.send_message(message.text)
    return "OK"


# Following code must be moved or removed
facebook_verification_token = environ["FACEBOOK_VERIFICATION_TOKEN"]


@app.get(webhook_path)
async def facebook_subscribe(mode: str = Query(None, alias="hub.mode"),
                             verify_token: str = Query(None, alias="hub.verify_token"),
                             challenge: int = Query(None, alias="hub.challenge")):
    if verify_token == facebook_verification_token and mode == "subscribe":
        return challenge
    raise HTTPException(status_code=403, detail="Invalid key")
