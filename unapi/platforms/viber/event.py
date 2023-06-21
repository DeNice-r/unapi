import hashlib
import hmac
import json
from typing import List

from starlette.requests import Request

from unapi.attachment import Attachment, AttachmentType
from unapi.event import Event
from unapi.platforms.viber import api
from unapi.platforms.viber.model import Model

from os import environ, path

viber_token = environ["VIBER_TOKEN"]


class ViberEvent(Event):
    original: Model  # this is needed to tell pydantic that original is a Model

    @property
    def chat_id(self) -> int | str:
        return self.original.sender.id

    @property
    def text(self) -> str:
        return self.original.message.text

    def _get_attachments(self) -> List[Attachment]:
        attachments = []
        message = self.original.message

        if message.file_name is None:
            return attachments

        file_name = path.splitext(message.file_name)

        # Viber has picture instead of image, so we need to map it
        attachment_type_mapping = {
            'picture': AttachmentType.Image.value
        }

        _type = message.type
        if _type in attachment_type_mapping:
            attachment_type = AttachmentType(attachment_type_mapping[_type])
        else:
            try:
                attachment_type = AttachmentType(_type)
            except ValueError:
                return attachments

        attachments.append(
            Attachment(
                name=file_name[0],
                extension=file_name[-1],
                type_=attachment_type,
                url=message.media
            )
        )
        return attachments

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
