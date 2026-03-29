from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from codejump.core.models import HistoryState
from codejump.utils.paths import HISTORY_FILE, ensure_runtime_dirs


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


class HistoryStore:
    def load(self) -> HistoryState:
        ensure_runtime_dirs()
        payload = _read_json(HISTORY_FILE)
        return HistoryState.from_dict(payload)

    def save(self, history: HistoryState) -> None:
        _write_json(HISTORY_FILE, history.to_dict())

