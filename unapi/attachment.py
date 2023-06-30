from enum import Enum
from pydantic import BaseModel


class AttachmentType(Enum):
    Image = 'image'
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

    @property
    def full_name(self) -> str:
        if self.extension:
            return f'{self.name}.{self.extension}'
        return self.name

    # Downloading method. May be overridden in subclasses
    def download(self, save=True) -> str | bytes | None:
        return download_attachment(self, save)


from unapi.util import download_attachment
