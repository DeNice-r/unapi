import logging
from uuid import uuid4
from os import environ, path
from datetime import datetime
from urllib.parse import urljoin as _urljoin
from abc import ABC
from typing import Type, Any, TypeVar
import base64
import requests
from pydantic.typing import PathLike


local_storage_path = environ["LOCAL_STORAGE_PATH"]


def webhook_urljoin(base: str, path: str) -> str:
    if base[-1] != "/":
        base += "/"
    if base[0] != "/":
        base = "/" + base
    return _urljoin(base, path)


def base64_encode(string: str) -> str:
    """
    Removes any `=` used as padding from the encoded string.
    """
    encoded = base64.urlsafe_b64encode(string.encode("utf-8")).decode("utf-8")
    return encoded.rstrip("=")


def base64_decode(string: str) -> str:
    """
    Adds back in the required padding before decoding.
    """
    padding = 4 - (len(string) % 4)
    string = string + ("=" * padding)
    return base64.urlsafe_b64decode(string.encode("utf-8")).decode("utf-8")


def generate_file_path(file_name: str, file_type: str) -> str:
    extension = path.splitext(file_name)[-1]
    local_path = path.join(
        local_storage_path,
        file_type,
        datetime.now().strftime("%d.%m.%Y_%H-%M-%S") + '_' + str(uuid4()) + extension)
    return path.normpath(local_path)


def save_file(file_path: str, file_content: bytes) -> str | None:
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        return file_path
    except FileNotFoundError:
        logging.error(f"Error: could not find file path {file_path}.")
    except IsADirectoryError:
        logging.error(f"Error: {file_path} is a directory.")
    except PermissionError:
        logging.error(f"Error: permission denied for {file_path}.")
    except Exception as e:
        logging.error(f"Error: an unexpected error occurred while saving the file:\n{e}")


def save_image(file_name: str, file_content: bytes) -> str:
    local_path = generate_file_path(file_name, AttachmentType.Photo.value)
    return save_file(local_path, file_content) or ""


def download_file(url: str) -> bytes | None:
    try:
        response = requests.get(url)
        if response.ok:
            return response.content
    except Exception as e:
        logging.error(f"Error: an unexpected error occurred while downloading the file:\n{e}")
    return None


def download_attachment(attachment: 'Attachment', save=True) -> str | bytes | None:
    if save:
        path = generate_file_path(f'{attachment.name}.{attachment.extension}', attachment.type_.value)
        return save_file(path, download_file(attachment.url))
    return download_file(attachment.url)


T = TypeVar("T")


class NoPublicConstructor(type):
    """
    Metaclass that ensures a private constructor

    If a class uses this metaclass like this:

        class SomeClass(metaclass=NoPublicConstructor):
            pass

    If you try to instantiate your class (`SomeClass()`),
    a `TypeError` will be thrown.
    """

    def __call__(cls, *args, **kwargs):
        raise TypeError(
            f"{cls.__module__}.{cls.__qualname__} has no public constructor"
        )

    def _create(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        return super().__call__(*args, **kwargs)  # type: ignore


class AbcNoPublicConstructor(ABC, NoPublicConstructor):
    """
    A class to use as a metaclass that inherits both ABC and NoPublicConstructor
    """
    pass


from unapi.attachment import AttachmentType, Attachment
