import hashlib
import hmac
import json

from starlette.requests import Request

from unapi.event import Event
from unapi.platforms.facebook import api
from unapi.platforms.facebook.model import Model

from os import environ

facebook_verification_token = environ["FACEBOOK_VERIFICATION_TOKEN"]
facebook_app_secret = environ["FACEBOOK_APP_SECRET"]


class FacebookEvent(Event):
    original: Model  # this is needed to tell pydantic that original is a Model

    @property
    def chat_id(self) -> int | str:
        return self.original.entry[0].messaging[0].sender.id

    @property
    def text(self) -> str:
        return self.original.entry[0].messaging[0].message.text

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
    def is_json_valid(json_data: dict) -> Model | None:
        try:
            return Model(**json_data)
        except:
            return None

    def send_message(self, text) -> None:
        api.send_message(self.chat_id, text)
