from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from codejump.core.enums import ItemType, SymbolKind, ThemeMode


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()


@dataclass(slots=True)
class WindowGeometry:
    width: int
    height: int
    left: int
    top: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "left": self.left,
            "top": self.top,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> WindowGeometry | None:
        if not payload:
            return None
        try:
            return cls(
                width=int(payload["width"]),
                height=int(payload["height"]),
                left=int(payload["left"]),
                top=int(payload["top"]),
            )
        except (KeyError, TypeError, ValueError):
            return None


@dataclass(slots=True)
class Settings:
    theme: ThemeMode = ThemeMode.DARK
    remember_window_geometry: bool = True
    start_with_last_project: bool = True
    start_with_last_query: bool = False
    always_on_top: bool = True
    max_visible_results: int = 40
    selected_project_id: str | None = None
    last_query: str = ""
    window_geometry: WindowGeometry | None = None
    default_editor_command: str = "code"

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme.value,
            "remember_window_geometry": self.remember_window_geometry,
            "start_with_last_project": self.start_with_last_project,
            "start_with_last_query": self.start_with_last_query,
            "always_on_top": self.always_on_top,
            "max_visible_results": self.max_visible_results,
            "selected_project_id": self.selected_project_id,
            "last_query": self.last_query,
            "window_geometry": self.window_geometry.to_dict() if self.window_geometry else None,
            "default_editor_command": self.default_editor_command,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> Settings:
        if not payload:
            return cls()
        return cls(
            theme=ThemeMode(payload.get("theme", ThemeMode.DARK.value)),
            remember_window_geometry=bool(payload.get("remember_window_geometry", True)),
            start_with_last_project=bool(payload.get("start_with_last_project", True)),
            start_with_last_query=bool(payload.get("start_with_last_query", False)),
            always_on_top=bool(payload.get("always_on_top", True)),
            max_visible_results=int(payload.get("max_visible_results", 40)),
            selected_project_id=payload.get("selected_project_id"),
            last_query=str(payload.get("last_query", "")),
            window_geometry=WindowGeometry.from_dict(payload.get("window_geometry")),
            default_editor_command=str(payload.get("default_editor_command", "code")),
        )


@dataclass(slots=True)
class Project:
    name: str
    root_path: str
    editor_command: str = "code"
    priority_extensions: list[str] = field(default_factory=list)
    ignored_dirs: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)

    @property
    def root(self) -> Path:
        return Path(self.root_path).expanduser().resolve()

    @property
    def exists(self) -> bool:
        return self.root.exists() and self.root.is_dir()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "root_path": self.root_path,
            "editor_command": self.editor_command,
            "priority_extensions": self.priority_extensions,
            "ignored_dirs": self.ignored_dirs,
            "aliases": self.aliases,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> Project:
        return cls(
            id=str(payload.get("id") or uuid4().hex),
            name=str(payload.get("name", "")).strip(),
            root_path=str(payload.get("root_path", "")).strip(),
            editor_command=str(payload.get("editor_command", "code")).strip() or "code",
            priority_extensions=[str(value).strip() for value in payload.get("priority_extensions", []) if str(value).strip()],
            ignored_dirs=[str(value).strip() for value in payload.get("ignored_dirs", []) if str(value).strip()],
            aliases=[str(value).strip() for value in payload.get("aliases", []) if str(value).strip()],
        )


@dataclass(slots=True)
class IndexItem:
    project_id: str
    item_type: ItemType
    display_name: str
    relative_path: str
    full_path: str
    name_tokens: list[str]
    path_tokens: list[str]
    preview_tokens: list[str]
    preview: str = ""
    line: int | None = None
    symbol_kind: SymbolKind | None = None
    extension: str = ""
    id: str = field(default_factory=lambda: uuid4().hex)

    @property
    def item_key(self) -> str:
        line_part = f":{self.line}" if self.line else ""
        return f"{self.item_type.value}:{self.relative_path}{line_part}:{self.display_name}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "item_type": self.item_type.value,
            "display_name": self.display_name,
            "relative_path": self.relative_path,
            "full_path": self.full_path,
            "name_tokens": self.name_tokens,
            "path_tokens": self.path_tokens,
            "preview_tokens": self.preview_tokens,
            "preview": self.preview,
            "line": self.line,
            "symbol_kind": self.symbol_kind.value if self.symbol_kind else None,
            "extension": self.extension,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> IndexItem:
        symbol_kind = payload.get("symbol_kind")
        return cls(
            id=str(payload.get("id") or uuid4().hex),
            project_id=str(payload.get("project_id", "")),
            item_type=ItemType(payload["item_type"]),
            display_name=str(payload.get("display_name", "")),
            relative_path=str(payload.get("relative_path", "")),
            full_path=str(payload.get("full_path", "")),
            name_tokens=[str(value) for value in payload.get("name_tokens", [])],
            path_tokens=[str(value) for value in payload.get("path_tokens", [])],
            preview_tokens=[str(value) for value in payload.get("preview_tokens", [])],
            preview=str(payload.get("preview", "")),
            line=int(payload["line"]) if payload.get("line") is not None else None,
            symbol_kind=SymbolKind(symbol_kind) if symbol_kind else None,
            extension=str(payload.get("extension", "")),
        )


@dataclass(slots=True)
class ProjectIndex:
    project_id: str
    indexed_at: str
    items: list[IndexItem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "indexed_at": self.indexed_at,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> ProjectIndex | None:
        if not payload:
            return None
        items = [IndexItem.from_dict(item) for item in payload.get("items", [])]
        return cls(
            project_id=str(payload.get("project_id", "")),
            indexed_at=str(payload.get("indexed_at", _utc_now_iso())),
            items=items,
        )


@dataclass(slots=True)
class QueryHistoryEntry:
    query: str
    count: int = 1
    last_used_at: str = field(default_factory=_utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "count": self.count,
            "last_used_at": self.last_used_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> QueryHistoryEntry:
        return cls(
            query=str(payload.get("query", "")),
            count=int(payload.get("count", 1)),
            last_used_at=str(payload.get("last_used_at", _utc_now_iso())),
        )


@dataclass(slots=True)
class RecentOpenEntry:
    item_key: str
    project_id: str
    display_name: str
    relative_path: str
    item_type: ItemType
    line: int | None = None
    opened_at: str = field(default_factory=_utc_now_iso)
    count: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_key": self.item_key,
            "project_id": self.project_id,
            "display_name": self.display_name,
            "relative_path": self.relative_path,
            "item_type": self.item_type.value,
            "line": self.line,
            "opened_at": self.opened_at,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RecentOpenEntry:
        return cls(
            item_key=str(payload.get("item_key", "")),
            project_id=str(payload.get("project_id", "")),
            display_name=str(payload.get("display_name", "")),
            relative_path=str(payload.get("relative_path", "")),
            item_type=ItemType(payload.get("item_type", ItemType.FILE.value)),
            line=int(payload["line"]) if payload.get("line") is not None else None,
            opened_at=str(payload.get("opened_at", _utc_now_iso())),
            count=int(payload.get("count", 1)),
        )


@dataclass(slots=True)
class HistoryState:
    recent_queries: list[QueryHistoryEntry] = field(default_factory=list)
    recent_opens: list[RecentOpenEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recent_queries": [item.to_dict() for item in self.recent_queries],
            "recent_opens": [item.to_dict() for item in self.recent_opens],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> HistoryState:
        if not payload:
            return cls()
        return cls(
            recent_queries=[QueryHistoryEntry.from_dict(item) for item in payload.get("recent_queries", [])],
            recent_opens=[RecentOpenEntry.from_dict(item) for item in payload.get("recent_opens", [])],
        )


@dataclass(slots=True)
class MatchExplanation:
    matched_tokens: list[str]
    reasons: list[str]
    score: float

    def summary(self) -> str:
        pieces: list[str] = []
        if self.matched_tokens:
            pieces.append(f"tokens: {', '.join(self.matched_tokens[:4])}")
        if self.reasons:
            pieces.append(" | ".join(self.reasons[:2]))
        return " · ".join(piece for piece in pieces if piece)


@dataclass(slots=True)
class SearchResult:
    item: IndexItem
    score: float
    explanation: MatchExplanation


@dataclass(slots=True)
class OpenResult:
    success: bool
    message: str

