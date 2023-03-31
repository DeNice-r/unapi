from enum import Enum
from typing import Union

from unapi.event_models import viber_model, telegram_model, facebook_model
from unapi.platforms import viber, telegram, facebook
from unapi.util import AbcNoPublicConstructor
from abc import abstractmethod
from fastapi import Request
from os import environ
import json
import hmac
import hashlib


telegram_verification_token = environ["TELEGRAM_VERIFICATION_TOKEN"]
viber_token = environ["VIBER_TOKEN"]
facebook_verification_token = environ["FACEBOOK_VERIFICATION_TOKEN"]
facebook_app_secret = environ["FACEBOOK_APP_SECRET"]


class MessengerType(Enum):
    TELEGRAM = 1
    VIBER = 2
    FACEBOOK = 3


class Event(metaclass=AbcNoPublicConstructor):
    """
    Event class for all messengers with a private constructor.
    It stores text, chat_id and original request body
    """
    text: str
    chat_id: str
    messenger_type: MessengerType
    original: dict

    def __init__(self, chat_id: str, text: str, messenger_type: MessengerType, original: dict) -> None:
        if not chat_id or not isinstance(chat_id, str):
            raise ValueError("chat_id must be a non-empty string")
        if not text or not isinstance(text, str):
            raise ValueError("text must be a non-empty string")
        if not isinstance(messenger_type, MessengerType):
            raise ValueError("messenger_type must be of type MessengerType")
        if not isinstance(original, dict):
            raise ValueError("original must be a dictionary")

        self.chat_id = chat_id
        self.text = text
        self.messenger_type = messenger_type
        self.original = original

    @classmethod
    async def create_if_valid(cls, request: Request) -> Union["Event", None]:
        """
        A class method that creates an event from json if it is valid
        :param request: an incoming request object
        :return: an event object or None if request is invalid
        """
        if await cls.is_request_valid(request):
            return cls.create(await request.json())
        return None

    @classmethod
    async def is_request_valid(cls, request: Request) -> bool:
        """
        A static method that checks if json is valid for this event
        :param request: an incoming request object
        :return: True if request is valid, False otherwise
        """
        return (await cls.is_request_authentic(request)) and cls.is_json_valid(await request.json())

    @staticmethod
    @abstractmethod
    async def is_request_authentic(request: Request) -> bool:
        """
        A static method that checks if request comes from a valid place
        :param request: an incoming request object
        :return: True if request is valid, False otherwise
        """
        pass

    @staticmethod
    @abstractmethod
    def is_json_valid(json_data: dict) -> bool:
        """
        A static method that checks if json is valid for this event
        :param json_data: an incoming request body in json format
        :return: True if json is valid, False otherwise
        """
        pass

    @abstractmethod
    def send_message(self, text: str) -> None:
        """
        A method that sends given message to the chat in the messenger the event was received from
        :param text: a message to send
        :return: None
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls, json_data: dict) -> "Event":
        """
        A class method that creates an event from json
        :param json_data: an incoming request body in json format
        :return: an event object
        """
        pass


class TelegramEvent(Event):
    @classmethod
    def create(cls, telegram_json: dict) -> "TelegramEvent":
        return cls._create(
            str(telegram_json["message"]["chat"]["id"]),
            telegram_json["message"]["text"],
            MessengerType.TELEGRAM,
            telegram_json
        )

    @staticmethod
    async def is_request_authentic(request: Request) -> bool:
        try:
            verification_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if telegram_verification_token == verification_token:
                return True
        except:
            return False
        return False

    @staticmethod
    def is_json_valid(json_data: dict) -> bool:
        try:
            telegram_model.Model(**json_data)
        except:
            return False
        return True

    def send_message(self, text) -> None:
        telegram.send_message(self.chat_id, text)


class ViberEvent(Event):
    @classmethod
    def create(cls, viber_json: dict) -> "ViberEvent":
        return cls._create(
            viber_json["sender"]["id"],
            viber_json["message"]["text"],
            MessengerType.VIBER,
            viber_json
        )

    @staticmethod
    async def is_request_authentic(request: Request) -> bool:
        try:
            raw_body = await request.body()
            body = json.loads(raw_body.decode("utf-8"))
            signature_hash = request.headers.get("X-Viber-Content-Signature")
            h = hmac.new(viber_token.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
            if signature_hash == h:
                return True
        except:
            return False
        return False

    @staticmethod
    def is_json_valid(json_data: dict) -> bool:
        try:
            viber_model.Model(**json_data)
        except:
            return False
        return True

    def send_message(self, text) -> None:
        viber.send_message(self.chat_id, text)


class FacebookEvent(Event):
    @classmethod
    def create(cls, facebook_json: dict) -> "FacebookEvent":
        return cls._create(
            facebook_json["entry"][0]["messaging"][0]["sender"]["id"],
            facebook_json["entry"][0]["messaging"][0]["message"]["text"],
            MessengerType.FACEBOOK,
            facebook_json
        )

    @staticmethod
    async def is_request_authentic(request: Request) -> bool:
        try:
            raw_body = await request.body()
            body = json.loads(raw_body.decode("utf-8"))
            signature_hash = request.headers.get("X-Hub-Signature-256").split("=")[1]
            h = hmac.new(facebook_app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
            if signature_hash == h and body["object"] == "page":
                return True
        except:
            return False
        return False

    @staticmethod
    def is_json_valid(json_data: dict) -> bool:
        try:
            facebook_model.Model(**json_data)
        except:
            return False
        return True

    def send_message(self, text) -> None:
        facebook.send_message(self.chat_id, text)


class EventFactory:
    @staticmethod
    async def create_event(request: Request) -> Event:
        """
        A static method that decides exact class for an event and creates it from json
        :param request: an incoming request object
        :return: an event object
        """
        for messenger in Event.__subclasses__():
            evt = await messenger.create_if_valid(request)
            if evt is None:
                continue
            return evt

        raise ValueError("Unknown messenger or the request is not authentic")
