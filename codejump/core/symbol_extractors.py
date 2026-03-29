from __future__ import annotations

import re
from dataclasses import dataclass

from codejump.core.enums import SymbolKind


@dataclass(slots=True)
class ExtractedSymbol:
    name: str
    line: int
    preview: str
    kind: SymbolKind


@dataclass(slots=True)
class SymbolPattern:
    pattern: re.Pattern[str]
    name_group: str | int
    kind: SymbolKind


MAX_SYMBOL_SCAN_LINES = 1200


DART_PATTERNS: tuple[SymbolPattern, ...] = (
    SymbolPattern(re.compile(r"^\s*class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"), "name", SymbolKind.CLASS),
    SymbolPattern(re.compile(r"^\s*enum\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"), "name", SymbolKind.ENUM),
    SymbolPattern(re.compile(r"^\s*extension\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"), "name", SymbolKind.EXTENSION),
    SymbolPattern(re.compile(r"^\s*typedef\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"), "name", SymbolKind.TYPEDEF),
    SymbolPattern(
        re.compile(
            r"^\s*class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+extends\s+(StatelessWidget|StatefulWidget)"
        ),
        "name",
        SymbolKind.WIDGET,
    ),
    SymbolPattern(
        re.compile(
            r"^\s*(?:[A-Za-z_<>\[\]?]+\s+)+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*\)\s*(?:async\s*)?\{?"
        ),
        "name",
        SymbolKind.FUNCTION,
    ),
)

PYTHON_PATTERNS: tuple[SymbolPattern, ...] = (
    SymbolPattern(re.compile(r"^\s*class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"), "name", SymbolKind.CLASS),
    SymbolPattern(re.compile(r"^\s*def\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\("), "name", SymbolKind.FUNCTION),
    SymbolPattern(re.compile(r"^\s*async\s+def\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\("), "name", SymbolKind.FUNCTION),
)

JS_TS_PATTERNS: tuple[SymbolPattern, ...] = (
    SymbolPattern(re.compile(r"^\s*function\s+(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)\s*\("), "name", SymbolKind.FUNCTION),
    SymbolPattern(
        re.compile(r"^\s*(?:export\s+)?const\s+(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)\s*="),
        "name",
        SymbolKind.CONSTANT,
    ),
    SymbolPattern(re.compile(r"^\s*class\s+(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)"), "name", SymbolKind.CLASS),
    SymbolPattern(re.compile(r"^\s*exports\.(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)\s*="), "name", SymbolKind.FUNCTION),
    SymbolPattern(re.compile(r"^\s*module\.exports\b"), 0, SymbolKind.MODULE),
    SymbolPattern(
        re.compile(r"^\s*(?:router|app)\.(get|post|put|delete)\s*\(\s*[\"']([^\"']+)[\"']"),
        2,
        SymbolKind.ROUTE,
    ),
)


SUPPORTED_EXTENSIONS = {
    ".dart": DART_PATTERNS,
    ".py": PYTHON_PATTERNS,
    ".js": JS_TS_PATTERNS,
    ".jsx": JS_TS_PATTERNS,
    ".ts": JS_TS_PATTERNS,
    ".tsx": JS_TS_PATTERNS,
}


def extract_symbols(content: str, extension: str) -> list[ExtractedSymbol]:
    patterns = SUPPORTED_EXTENSIONS.get(extension.lower())
    if not patterns:
        return []

    results: list[ExtractedSymbol] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        if line_number > MAX_SYMBOL_SCAN_LINES:
            break
        stripped = line.strip()
        if not stripped:
            continue
        for symbol_pattern in patterns:
            match = symbol_pattern.pattern.search(line)
            if not match:
                continue
            if symbol_pattern.name_group == 0:
                symbol_name = stripped[:80]
            else:
                symbol_name = match.group(symbol_pattern.name_group).strip()
            results.append(
                ExtractedSymbol(
                    name=symbol_name,
                    line=line_number,
                    preview=stripped[:160],
                    kind=symbol_pattern.kind,
                )
            )
            break
    return results

