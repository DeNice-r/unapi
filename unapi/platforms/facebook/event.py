import hashlib
import hmac
import json
from typing import List

from starlette.requests import Request

from unapi.event import Event
from unapi.attachment import Attachment, AttachmentType
from unapi.platforms.facebook import api
from unapi.platforms.facebook.model import Model

from os import environ, path

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

    def _get_attachments(self) -> List[Attachment]:
        attachments = []
        original_attachments = self.original.entry[0].messaging[0].message.attachments
        if original_attachments is None:
            return attachments
        for attachment in original_attachments:
            url = attachment.payload.url
            file_name = path.splitext(url.split('/')[-1].split('?')[0])

            # Facebook has image instead of photo, so we need to map it
            attachment_type_mapping = {
                'image': AttachmentType.Photo.value
            }

            _type = attachment.type
            if _type in attachment_type_mapping:
                attachment_type = AttachmentType(attachment_type_mapping[_type])
            else:
                try:
                    attachment_type = AttachmentType(_type)
                except ValueError:
                    continue

            attachments.append(
                Attachment(
                    name=file_name[0],
                    extension=file_name[-1],
                    type_=attachment_type,
                    url=url
                )
            )
        return attachments

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
