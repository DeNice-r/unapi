from pydantic import BaseModel
from starlette.requests import Request

from unapi.platforms.telegram import api
from unapi.platforms.telegram.model import Model
from unapi.event import Event

from os import environ

telegram_verification_token = environ["TELEGRAM_VERIFICATION_TOKEN"]


class TelegramEvent(Event):
    @classmethod
    def create(cls, data: Model) -> "TelegramEvent":
        return cls._create(
            data.message.chat.id,
            data.message.text,
            data
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
    def is_json_valid(json_data: dict) -> BaseModel | None:
        try:
            return Model(**json_data)
        except:
            return None

    def send_message(self, text) -> None:
        api.send_message(self.chat_id, text)
