from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from codejump.core.models import Settings
from codejump.utils.paths import SETTINGS_FILE, ensure_runtime_dirs


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_runtime_dirs()
    with NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as temp_file:
        json.dump(payload, temp_file, indent=2, ensure_ascii=False)
        temp_name = temp_file.name
    Path(temp_name).replace(path)


class SettingsStore:
    def load(self) -> Settings:
        ensure_runtime_dirs()
        payload = _read_json(SETTINGS_FILE)
        return Settings.from_dict(payload)

    def save(self, settings: Settings) -> None:
        _write_json(SETTINGS_FILE, settings.to_dict())

