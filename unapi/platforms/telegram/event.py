from starlette.requests import Request

from unapi.platforms.facebook import api
from unapi.platforms.telegram import model
from unapi.event import Event, MessengerType, telegram_verification_token


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
            model.Model(**json_data)
        except:
            return False
        return True

    def send_message(self, text) -> None:
        api.send_message(self.chat_id, text)
