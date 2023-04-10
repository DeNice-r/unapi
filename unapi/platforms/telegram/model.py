from pydantic import BaseModel, Field
from typing import Optional


class From(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: str
    language_code: str


class Chat(BaseModel):
    id: int
    first_name: str
    username: str
    type: str


class File(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: int
    width: int
    height: int


class Message(BaseModel):
    message_id: int
    from_: From = Field(..., alias='from')
    chat: Chat
    date: int
    text: str = Field(..., alias='caption')  # caption is used for photos
    # Must download file from telegram servers, save it to local storage and use own file class
    photo: list[File] | None

    class Config:
        allow_population_by_field_name = True


class Model(BaseModel):
    update_id: int
    message: Message
