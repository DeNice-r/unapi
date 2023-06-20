from pydantic import BaseModel


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


class Model(BaseModel):
    event: str
    timestamp: int
    chat_hostname: str
    message_token: int
    sender: Sender
    message: Message
    silent: bool
