import base64


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
