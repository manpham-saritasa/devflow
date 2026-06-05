from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    download_path: Path
    sync_state_path: Path
    not_found_state_path: Path
    template_paths: list[Path]
    custom_fields: dict[str, str]
    pending_tasks_path: Path
    pr_template_path: Path
    env_path: Path
