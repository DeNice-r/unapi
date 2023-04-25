import hashlib
import hmac
import json

from starlette.requests import Request

from unapi.event import Event
from unapi.platforms.viber import api
from unapi.platforms.viber.model import Model

from os import environ

viber_token = environ["VIBER_TOKEN"]


class ViberEvent(Event):
    original: Model  # this is needed to tell pydantic that original is a Model

    @property
    def chat_id(self) -> int | str:
        return self.original.sender.id

    @property
    def text(self) -> str:
        return self.original.message.text

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
    def is_json_valid(json_data: dict) -> Model | None:
        try:
            return Model(**json_data)
        except:
            return None

    def send_message(self, text) -> None:
        api.send_message(self.chat_id, text)
