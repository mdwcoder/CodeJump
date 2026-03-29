from __future__ import annotations

from enum import Enum


class ItemType(str, Enum):
    FILE = "file"
    FOLDER = "folder"
    SYMBOL = "symbol"


class SymbolKind(str, Enum):
    CLASS = "class"
    ENUM = "enum"
    EXTENSION = "extension"
    TYPEDEF = "typedef"
    FUNCTION = "function"
    ROUTE = "route"
    MODULE = "module"
    WIDGET = "widget"
    CONSTANT = "constant"


class ThemeMode(str, Enum):
    DARK = "dark"

