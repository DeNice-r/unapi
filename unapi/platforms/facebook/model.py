import logging
from typing import List

import requests
from pydantic import BaseModel, validator

from unapi.util import save_image


class Sender(BaseModel):
    id: str


class Recipient(BaseModel):
    id: str


class PayloadItem(BaseModel):
    url: str
    local_path: str | None = None


class AttachmentItem(BaseModel):
    type: str
    payload: PayloadItem

    @validator('payload')
    def download_attachment(cls, value):
        response = requests.get(value.url)
        if response.ok:
            file_path = response.url.split('/')[-1].split('?')[0]
            value.local_path = save_image(file_path, response.content)
        return value


class Message(BaseModel):
    mid: str
    text: str = ''
    attachments: List[AttachmentItem] | None


class MessagingItem(BaseModel):
    sender: Sender
    recipient: Recipient
    timestamp: int
    message: Message

    @validator('message')
    def validate_attachments(cls, value):
        if value.attachments is None:
            return value
        for attachment in value.attachments:
            if attachment.type not in ['image']:  # audio, video, file, location, fallback
                value.message.text = f'Message contains invalid attachment type: {value}'
                break
        return value


class EntryItem(BaseModel):
    id: str
    time: int
    messaging: List[MessagingItem]


class Model(BaseModel):
    object: str
    entry: List[EntryItem]
