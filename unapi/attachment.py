from enum import Enum
from pydantic import BaseModel


class AttachmentType(Enum):
    Photo = 'photo'
    Video = 'video'
    Audio = 'audio'
    File = 'file'
    Location = 'location'


class Attachment(BaseModel):
    name: str
    type: AttachmentType
    extension: str
    url: str

    # Downloading method
