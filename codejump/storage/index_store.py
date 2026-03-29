from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from codejump.core.models import ProjectIndex
from codejump.utils.paths import INDEX_CACHE_DIR, ensure_runtime_dirs


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


class IndexStore:
    def _project_file(self, project_id: str) -> Path:
        ensure_runtime_dirs()
        return INDEX_CACHE_DIR / f"{project_id}.json"

    def load(self, project_id: str) -> ProjectIndex | None:
        payload = _read_json(self._project_file(project_id))
        return ProjectIndex.from_dict(payload)

    def save(self, project_index: ProjectIndex) -> None:
        _write_json(self._project_file(project_index.project_id), project_index.to_dict())

    def delete(self, project_id: str) -> None:
        path = self._project_file(project_id)
        if path.exists():
            path.unlink()
