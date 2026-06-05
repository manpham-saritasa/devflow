from dataclasses import dataclass


@dataclass
class AttachmentInfo:
    filename: str
    url: str
    mime_type: str | None = None
    size: int | None = None
    created: str | None = None
    author_name: str | None = None
