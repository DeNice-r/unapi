from pydantic import BaseModel
from typing import Union

from unapi.util import AbcNoPublicConstructor
from abc import abstractmethod
from fastapi import Request
from os import environ


class Event(metaclass=AbcNoPublicConstructor):
    """
    Event class for all messengers with a private constructor.
    It stores text, chat_id and original request body
    """
    text: str
    chat_id: int | str
    original: BaseModel

    def __init__(self, chat_id: str, text: str, original: BaseModel) -> None:
        if not chat_id or not (isinstance(chat_id, str) or isinstance(chat_id, int)):
            raise ValueError("chat_id must be a non-empty string or a non-zero integer, depending on a messenger")
        if not text or not isinstance(text, str):
            raise ValueError("text must be a non-empty string")
        if not isinstance(original, BaseModel):
            raise ValueError("original must be a pydantic BaseModel subclass")

        self.chat_id = chat_id
        self.text = text
        self.original = original

    @classmethod
    async def create_if_valid(cls, request: Request) -> Union["Event", None]:
        """
        A class method that creates an event from json if it is valid
        :param request: an incoming request object
        :return: an event object or None if request is invalid
        """
        data = await cls.is_request_valid(request)
        if data:
            return cls.create(data)
        return None

    @classmethod
    async def is_request_valid(cls, request: Request) -> BaseModel | None:
        """
        A static method that checks if json is valid for this event
        :param request: an incoming request object
        :return: True if request is valid, False otherwise
        """
        return (await cls.is_request_authentic(request)) and cls.is_json_valid(await request.json())

    @staticmethod
    @abstractmethod
    async def is_request_authentic(request: Request) -> bool:
        """
        A static method that checks if request comes from a valid place
        :param request: an incoming request object
        :return: True if request is valid, False otherwise
        """
        raise NotImplementedError("is_request_authentic is a subclass-implemented method")

    @staticmethod
    @abstractmethod
    def is_json_valid(json_data: dict) -> BaseModel | None:
        """
        A static method that checks if json is valid for this event
        :param json_data: an incoming request body in json format
        :return: True if json is valid, False otherwise
        """
        raise NotImplementedError("is_json_valid is a subclass-implemented method")

    @abstractmethod
    def send_message(self, text: str) -> None:
        """
        A method that sends given message to the chat in the messenger the event was received from
        :param text: a message to send
        :return: None
        """
        raise NotImplementedError("send_message is a subclass-implemented method")

    @classmethod
    @abstractmethod
    def create(cls, data: BaseModel) -> "Event":
        """
        A class method that creates an event from json
        :param data: an incoming request body, already checked for validity and in pydantic model format
        :return: an event object
        """
        raise NotImplementedError("create is a subclass-implemented method")


class EventFactory:
    @staticmethod
    async def create_event(request: Request) -> Event:
        """
        A static method that decides exact class for an event and creates it from json
        :param request: an incoming request object
        :return: an event object
        """
        for messenger in Event.__subclasses__():
            evt = await messenger.create_if_valid(request)
            if evt is None:
                continue
            return evt

        raise ValueError("Unknown request origin")
