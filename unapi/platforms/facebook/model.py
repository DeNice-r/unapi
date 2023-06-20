from typing import List
from pydantic import BaseModel


class Sender(BaseModel):
    id: str


class Recipient(BaseModel):
    id: str


class PayloadItem(BaseModel):
    url: str


class AttachmentItem(BaseModel):
    type: str
    payload: PayloadItem


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
