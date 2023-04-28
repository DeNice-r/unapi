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

    @validator('type')
    def validate_type(cls, v):
        if v not in ['image']:  # audio, video, file, location, fallback
            message = f'Invalid attachment type: {v}'
            logging.error(message)
            raise ValueError(message)
        return v

    @validator('payload')
    def validate_payload(cls, v):
        if not v:
            raise ValueError('Payload is empty')

        response = requests.get(v.url)
        if response.ok:
            file_path = response.url.split('/')[-1].split('?')[0]
            v.local_path = save_image(file_path, response.content)
        return v


class Message(BaseModel):
    mid: str
    text: str = ''
    attachments: List[AttachmentItem] | None


class MessagingItem(BaseModel):
    sender: Sender
    recipient: Recipient
    timestamp: int
    message: Message


class EntryItem(BaseModel):
    id: str
    time: int
    messaging: List[MessagingItem]


class Model(BaseModel):
    object: str
    entry: List[EntryItem]
