from enum import Enum

from unapi.platforms import viber, telegram, facebook
from unapi.event_models import viber_model, telegram_model, facebook_model
from unapi.util import NoPublicConstructor
from abc import ABC, abstractmethod


class MessengerType(Enum):
    TELEGRAM = 1
    VIBER = 2
    FACEBOOK = 3


class AbcNoPublicConstructor(ABC, NoPublicConstructor):
    """
    A class to use as a metaclass for Event that inherits both ABC and NoPublicConstructor
    """
    pass


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

    @staticmethod
    @abstractmethod
    def is_json_valid(json_data: dict) -> bool:
        """
        A static method that checks if json is valid for this event
        :param json_data:
        :return:
        """
        pass

    @abstractmethod
    def send_message(self, text: str) -> None:
        """
        A method that sends given message to the chat in the messenger the event was received from
        :param text:
        :return:
        """
        pass

    @classmethod
    @abstractmethod
    def create(cls, json_data: dict) -> "Event":
        """
        A class method that creates an event from json
        :param json_data:
        :return:
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
    def create_event(json_data: dict) -> Event:
        """
        A static method that decides exact class for an event and creates it from json
        :param json_data:
        :return:
        """
        for messenger in Event.__subclasses__():
            if messenger.is_json_valid(json_data):
                return messenger.create(json_data)
        raise ValueError("Unknown messenger")
