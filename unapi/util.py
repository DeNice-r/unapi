from urllib.parse import urljoin as _urljoin

from typing import Type, Any, TypeVar

import base64


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
