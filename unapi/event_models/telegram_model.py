from pydantic import BaseModel, Field


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


class Message(BaseModel):
    message_id: int
    from_: From = Field(..., alias='from')
    chat: Chat
    date: int
    text: str


class Model(BaseModel):
    update_id: int
    message: Message
