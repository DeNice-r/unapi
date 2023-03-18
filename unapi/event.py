from enum import Enum
from unapi.util import NoPublicConstructor


class RequestType(Enum):
    TELEGRAM = 1
    VIBER = 2
    FACEBOOK = 3


class Event(metaclass=NoPublicConstructor):
    """
    Message class for all messengers with a private constructor and public classmethods for each messenger
    It stores text, chat_id, request_type and original request body
    """
    text: str
    chat_id: str
    request_type: RequestType
    original: dict

    def __init__(self, chat_id: str, text: str, request_type: RequestType, original: dict) -> "Event":
        self.chat_id = chat_id
        self.text = text
        self.request_type = request_type
        self.original = original

    @classmethod
    def from_telegram(cls, telegram_json: dict) -> "Event":
        return cls._create(
            str(telegram_json["message"]["chat"]["id"]),
            telegram_json["message"]["text"],
            RequestType.TELEGRAM,
            telegram_json
        )

    @classmethod
    def from_viber(cls, viber_json: dict) -> "Event":
        return cls._create(
            viber_json["sender"]["id"],
            viber_json["message"]["text"],
            RequestType.VIBER,
            viber_json
        )

    @classmethod
    def from_facebook(cls, facebook_json: dict) -> "Event":
        return cls._create(
            facebook_json["entry"][0]["messaging"][0]["sender"]["id"],
            facebook_json["entry"][0]["messaging"][0]["message"]["text"],
            RequestType.FACEBOOK,
            facebook_json
        )