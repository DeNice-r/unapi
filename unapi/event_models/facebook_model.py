from typing import List
from pydantic import BaseModel


class Sender(BaseModel):
    id: str


class Recipient(BaseModel):
    id: str


class Message(BaseModel):
    mid: str
    text: str


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
