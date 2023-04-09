import hashlib
import hmac
import json

from starlette.requests import Request

from unapi.event import Event, MessengerType, viber_token
from unapi.platforms.viber import api, model


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
            model.Model(**json_data)
        except:
            return False
        return True

    def send_message(self, text) -> None:
        api.send_message(self.chat_id, text)
