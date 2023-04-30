import requests
from pydantic import BaseModel, validator

from unapi.util import save_image


class Sender(BaseModel):
    id: str
    name: str
    avatar: str
    language: str
    country: str
    api_version: int


class Message(BaseModel):
    type: str
    text: str | None
    media: str | None
    thumbnail: str | None
    file_name: str | None
    size: int | None
    local_path: str | None


class Model(BaseModel):
    event: str
    timestamp: int
    chat_hostname: str
    message_token: int
    sender: Sender
    message: Message
    silent: bool

    @validator('message')
    def download_attachment(cls, value):
        if value.type == 'picture':
            response = requests.get(value.media)
            if response.ok:
                file_path = value.file_name
                value.local_path = save_image(file_path, response.content)
        elif value.type != 'text':
            value.text = f'Unsupported message type: {value.type}'
        return value

