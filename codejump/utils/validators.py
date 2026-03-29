from __future__ import annotations

from pathlib import Path


def split_config_list(raw_value: str) -> list[str]:
    chunks = []
    for part in raw_value.replace("\n", ",").split(","):
        cleaned = part.strip()
        if cleaned:
            chunks.append(cleaned)
    return chunks


def is_existing_directory(path_value: str) -> bool:
    if not path_value.strip():
        return False
    return Path(path_value).expanduser().exists() and Path(path_value).expanduser().is_dir()


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))

