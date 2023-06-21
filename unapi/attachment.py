from enum import Enum
from pydantic import BaseModel
from unapi.util import download_attachment


class AttachmentType(Enum):
    Photo = 'photo'
    Video = 'video'
    Audio = 'audio'
    File = 'file'
    Location = 'location'


class Attachment(BaseModel):
    # TODO: consider adding a new type for unsupported attachments
    name: str
    type_: AttachmentType
    extension: str
    url: str

    # Downloading method. May be overridden in subclasses
    def download(self, save=True) -> str | bytes | None:
        return download_attachment(self, save)
