import requests
from pydantic import BaseModel
from starlette.requests import Request

from unapi.attachment import Attachment, AttachmentType
from unapi.platforms.telegram import api
from unapi.platforms.telegram.model import Model
from unapi.event import Event

from os import environ

telegram_verification_token = environ["TELEGRAM_VERIFICATION_TOKEN"]
telegram_token = environ["TELEGRAM_TOKEN"]


class TelegramEvent(Event):
    original: Model  # this is needed to tell pydantic that original is a Model

    @property
    def chat_id(self) -> int | str:
        return self.original.message.chat.id

    @property
    def text(self) -> str:
        return self.original.message.text

    def get_attachments(self) -> list:
        attachments = []
        file_id = self.original.message.photo[-1].file_id
        file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
        response_json = requests.get(file_url).json()
        if not response_json["ok"]:
            raise ValueError('Error getting file path')
        file_path = response_json["result"]["file_path"]
        file_name = file_path.split('/')[-1].split('.')
        attachments.append(
            Attachment(
                name=file_name[0],
                extension=file_name[-1],
                type=AttachmentType('photo'),
                url=f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
            )
        )
        return attachments

    # Telegram attachment downloading example:

    # @validator('photo')
    # def download_attachment(cls, value):
    #     if value is None:
    #         return value
    #
    #     photo = value[-1]  # Only last variant is used as it is the biggest one
    #     if photo.local_path:
    #         return value
    #     file_id = photo.file_id
    #     file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
    #     response = requests.get(file_url)
    #     response_json = response.json()
    #
    #     if response_json["ok"]:
    #         file_path = response_json["result"]["file_path"]
    #         file_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
    #         response = requests.get(file_url)
    #
    #         if response.ok:
    #             photo.local_path = save_image(file_path, response.content)
    #         else:
    #             raise ValueError(f"Error downloading file: {response.status_code} {response.reason}")
    #     else:
    #         raise ValueError(
    #             f"Error getting file path: {response_json['error_code']} {response_json['description']}")
    #
    #     return value

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
