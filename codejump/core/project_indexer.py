from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from codejump.core.enums import ItemType
from codejump.core.models import IndexItem, Project, ProjectIndex
from codejump.core.symbol_extractors import extract_symbols
from codejump.core.tokenizer import unique_tokens


LOGGER = logging.getLogger(__name__)

DEFAULT_IGNORED_DIRS = {
    ".git",
    "node_modules",
    "build",
    "dist",
    ".dart_tool",
    ".next",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
    "ios/Pods",
    "android/.gradle",
}

TEXT_PREVIEW_EXTENSIONS = {
    ".py",
    ".dart",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".yaml",
    ".yml",
    ".txt",
    ".php",
    ".css",
    ".scss",
    ".html",
}

MAX_TEXT_BYTES = 48_000
MAX_FILE_SIZE_BYTES = 2_000_000


class ProjectIndexer:
    def build_index(self, project: Project) -> ProjectIndex:
        items: list[IndexItem] = []
        root = project.root
        ignored_dirs = self._build_ignored_set(project)
        if not root.exists():
            return ProjectIndex(project_id=project.id, indexed_at=self._now(), items=items)

        for current_root_str, dirs, files in os.walk(root, topdown=True):
            current_root = Path(current_root_str)
            rel_dir = self._relative_path(root, current_root)
            dirs[:] = [
                folder_name
                for folder_name in dirs
                if not self._should_ignore_dir(rel_dir, folder_name, ignored_dirs)
            ]

            if rel_dir != ".":
                folder_path = Path(rel_dir)
                items.append(
                    self._make_item(
                        project_id=project.id,
                        item_type=ItemType.FOLDER,
                        root=root,
                        path=root / folder_path,
                        display_name=folder_path.name,
                        preview="folder",
                    )
                )

            for file_name in files:
                full_path = current_root / file_name
                extension = full_path.suffix.lower()
                file_text = self._read_text_sample(full_path)
                preview = self._build_preview(file_text)
                items.append(
                    self._make_item(
                        project_id=project.id,
                        item_type=ItemType.FILE,
                        root=root,
                        path=full_path,
                        display_name=file_name,
                        preview=preview,
                        extension=extension,
                    )
                )

                if file_text and extension:
                    for symbol in extract_symbols(file_text, extension):
                        items.append(
                            self._make_item(
                                project_id=project.id,
                                item_type=ItemType.SYMBOL,
                                root=root,
                                path=full_path,
                                display_name=symbol.name,
                                preview=symbol.preview,
                                line=symbol.line,
                                symbol_kind=symbol.kind,
                                extension=extension,
                            )
                        )

        return ProjectIndex(project_id=project.id, indexed_at=self._now(), items=items)

    def _make_item(
        self,
        project_id: str,
        item_type: ItemType,
        root: Path,
        path: Path,
        display_name: str,
        preview: str = "",
        line: int | None = None,
        symbol_kind=None,
        extension: str = "",
    ) -> IndexItem:
        relative_path = self._relative_path(root, path)
        return IndexItem(
            project_id=project_id,
            item_type=item_type,
            display_name=display_name,
            relative_path=relative_path,
            full_path=str(path),
            name_tokens=unique_tokens(display_name),
            path_tokens=unique_tokens(relative_path),
            preview_tokens=unique_tokens(preview),
            preview=preview,
            line=line,
            symbol_kind=symbol_kind,
            extension=extension,
        )

    def _build_ignored_set(self, project: Project) -> set[str]:
        merged = set(DEFAULT_IGNORED_DIRS)
        merged.update(project.ignored_dirs)
        return {value.strip().strip("/") for value in merged if value.strip()}

    def _should_ignore_dir(self, rel_dir: str, folder_name: str, ignored_dirs: set[str]) -> bool:
        candidates = {
            folder_name,
            f"{rel_dir}/{folder_name}".strip("./"),
        }
        for candidate in candidates:
            normalized = candidate.strip("/")
            if normalized in ignored_dirs:
                return True
        return False

    def _read_text_sample(self, path: Path) -> str:
        try:
            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                return ""
        except OSError:
            return ""

        try:
            chunk = path.read_bytes()[:MAX_TEXT_BYTES]
            if b"\x00" in chunk:
                return ""
            text = chunk.decode("utf-8", errors="ignore")
        except OSError as exc:
            LOGGER.debug("Skipping preview for %s: %s", path, exc)
            return ""

        return text

    def _build_preview(self, text: str) -> str:
        if not text:
            return ""
        preview_lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                preview_lines.append(stripped)
            if len(preview_lines) >= 6:
                break
        return " ".join(preview_lines)[:320]

    def _relative_path(self, root: Path, path: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)

    def _now(self) -> str:
        return datetime.utcnow().replace(microsecond=0).isoformat()
