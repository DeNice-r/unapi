import logging
from urllib.parse import urljoin
from os import environ

import asyncio
import aiohttp

telegram_token = environ["TELEGRAM_TOKEN"]
telegram_verification_token = environ["TELEGRAM_VERIFICATION_TOKEN"]
viber_token = environ["VIBER_TOKEN"]
facebook_api_version = environ["FACEBOOK_API_VERSION"]
facebook_verification_token = environ["FACEBOOK_VERIFICATION_TOKEN"]
facebook_page_token = environ["FACEBOOK_PAGE_TOKEN"]
api_url = environ["API_URL"]
webhook_path = environ["WEBHOOK_PATH"]


async def set_webhook(url, headers, body) -> (bool, dict):
    """
    Asynchronously post to `url` with `headers` and `body`
    :param url: url of API endpoint
    :param headers: a set of headers to add to the request
    :param body: body of the request
    :return: bool - status of the request, dict - body of the response
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as resp:
            resp_body = await resp.json()
            return (
                resp.status == 200,
                resp_body
            )


async def set_telegram_webhook() -> None:
    """
    Set webhook for Telegram
    :return:
    """
    url = f"https://api.telegram.org/bot{telegram_token}/setWebhook"
    headers = {}
    body = {
        "url": urljoin(api_url, webhook_path),
        "allowed_updates": "message",
        "secret_token": telegram_verification_token,
    }

    status, json = await set_webhook(url, headers, body)

    if status and json["ok"]:
        logging.info("Telegram webhook set")
    else:
        logging.warning("Telegram webhook not set")


async def set_viber_webhook() -> None:
    """
    Set webhook for Viber
    :return:
    """
    url = "https://chatapi.viber.com/pa/set_webhook"
    headers = {
        "X-Viber-Auth-Token": viber_token,
        "Content-Type": "application/json",
    }
    body = {
        "url": urljoin(api_url, webhook_path),
        "event_types": [
            "conversation_started",
            "message",
            "seen"
        ],
        "send_name": False,
        "send_photo": False
    }

    status, json = await set_webhook(url, headers, body)

    if status and json["status"] == 0:
        logging.info("Viber webhook set")
    else:
        logging.warning("Viber webhook not set")


async def set_facebook_webhook() -> None:
    """
    Set webhook for Facebook
    :return:
    """
    url = f"https://graph.facebook.com/v{facebook_api_version}/me/subscribed_apps"
    headers = {}
    body = {
        "access_token": facebook_page_token,
        "subscribed_fields": "messages, message_deliveries",
        "callback_url": urljoin(api_url, webhook_path),
        "verify_token": facebook_verification_token
    }

    status, json = await set_webhook(url, headers, body)

    if status and json["success"]:
        logging.info("Facebook webhook set")
    else:
        logging.warning("Facebook webhook not set")


async def init() -> None:
    """
    Set webhooks for all platforms
    :return:
    """
    await asyncio.gather(
        set_telegram_webhook(),
        set_viber_webhook(),
        set_facebook_webhook()
    )
