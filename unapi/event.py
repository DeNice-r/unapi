from pydantic import BaseModel
from typing import Union, List

from unapi.util import AbcNoPublicConstructor
from unapi.attachment import Attachment

from abc import abstractmethod
from fastapi import Request
from os import environ


class Event(metaclass=AbcNoPublicConstructor):
    """
    Event class for all messengers with a private constructor.
    It stores text, chat_id and original request body
    """
    original: BaseModel
    __attachments: List[Attachment] | None = None

    def __init__(self, original: BaseModel) -> None:
        if not isinstance(original, BaseModel):
            raise ValueError("original must be a pydantic BaseModel subclass")

        self.original = original

    @classmethod
    def create(cls, data: BaseModel) -> "Event":
        """
        A class method that creates an event from respective pydantic model
        :param data: an incoming request body, already checked for validity and in pydantic model format
        :return: an event object
        """
        if cls is Event:
            raise NotImplementedError("create should never be called on Event directly")
        return cls._create(data)

    @property
    @abstractmethod
    def chat_id(self) -> int | str:
        """
        A property that returns a chat id
        :return: a chat id
        """
        raise NotImplementedError("chat_id is a subclass-implemented property")

    @property
    @abstractmethod
    def text(self) -> str:
        """
        A property that returns message text
        :return: a text
        """
        raise NotImplementedError("text is a subclass-implemented property")

    @property
    @abstractmethod
    def attachments(self) -> List[Attachment]:
        """
        A property that returns message attachments
        :return: List[Attachment]
        """
        if self.__attachments is None:
            self.__attachments = self._get_attachments()

        return self.__attachments

    @abstractmethod
    def _get_attachments(self) -> List[Attachment]:
        """
        A method that gathers message attachments
        :return: List[Attachment]
        """
        raise NotImplementedError("text is a subclass-implemented property")

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
