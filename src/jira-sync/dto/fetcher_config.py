from dataclasses import dataclass
from pathlib import Path


@dataclass
class FetcherConfig:
    domain: str
    email: str
    token: str
    project_key: str = ""
    fields: list[str] | None = None
    custom_fields: dict[str, str] | None = None
    template_paths: list[Path] | None = None
    timeout: int = 30
