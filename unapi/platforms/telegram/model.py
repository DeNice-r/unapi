import os
import uuid

import requests
from pydantic import BaseModel, Field, validator
from typing import List
from os import environ


telegram_token = environ["TELEGRAM_TOKEN"]
local_storage_path = environ["LOCAL_STORAGE_PATH"]


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


class PhotoItem(BaseModel):
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
    text: str = Field(default='-', alias='caption')  # caption is used for photos
    # Must download file from telegram servers, save it to local storage and use own file class
    photo: List[PhotoItem] | None

    class Config:
        allow_population_by_field_name = True

    @validator('photo')
    def validate_photo(cls, value, values):
        if not value:
            return value

        print('Starting photo validation')
        photo = value[-1]
        file_id = photo.file_id
        file_url = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
        response = requests.get(file_url)
        response_json = response.json()

        if response_json["ok"]:
            file_path = response_json["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
            response = requests.get(file_url)

            if response.ok:
                extension = os.path.splitext(file_path)[-1]
                local_file_path = os.path.join(os.getcwd(), local_storage_path, 'images', str(uuid.uuid4()) + extension)
                with open(local_file_path, 'wb') as f:
                    f.write(response.content)
                print('Ending photo validation')
            else:
                raise ValueError(f"Error downloading file: {response.status_code} {response.reason}")
        else:
            raise ValueError(f"Error getting file path: {response_json['error_code']} {response_json['description']}")

        return values


class Model(BaseModel):
    update_id: int
    message: Message
