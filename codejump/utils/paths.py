from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PACKAGE_ROOT / "config"
DATA_DIR = PACKAGE_ROOT / "data"
INDEX_CACHE_DIR = DATA_DIR / "index_cache"
ASSETS_DIR = PACKAGE_ROOT / "assets"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
PROJECTS_FILE = CONFIG_DIR / "projects.json"
HISTORY_FILE = DATA_DIR / "history.json"


def ensure_runtime_dirs() -> None:
    for path in (CONFIG_DIR, DATA_DIR, INDEX_CACHE_DIR, ASSETS_DIR):
        path.mkdir(parents=True, exist_ok=True)

