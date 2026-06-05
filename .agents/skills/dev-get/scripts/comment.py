from dataclasses import dataclass


@dataclass
class Comment:
    author: str
    created: str
    body_text: str
