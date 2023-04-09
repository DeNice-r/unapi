import hashlib
import hmac
import json

from starlette.requests import Request

from unapi.event import Event, MessengerType, facebook_app_secret
from unapi.platforms.facebook import api
from unapi.platforms.facebook import model


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
            model.Model(**json_data)
        except:
            return False
        return True

    def send_message(self, text) -> None:
        api.send_message(self.chat_id, text)
