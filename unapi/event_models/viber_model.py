from pydantic import BaseModel


class Sender(BaseModel):
    id: str
    name: str
    avatar: str
    language: str
    country: str
    api_version: int


class Message(BaseModel):
    text: str
    type: str


class Model(BaseModel):
    event: str
    timestamp: int
    chat_hostname: str
    message_token: int
    sender: Sender
    message: Message
    silent: bool
