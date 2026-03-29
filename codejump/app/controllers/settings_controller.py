from __future__ import annotations

from codejump.core.geometry import default_overlay_geometry, sanitize_geometry
from codejump.core.models import Settings, WindowGeometry
from codejump.storage.settings_store import SettingsStore
from codejump.utils.platform_helpers import get_screen_size


class SettingsController:
    def __init__(self, store: SettingsStore) -> None:
        self.store = store
        self.settings = self.store.load()

    def persist(self) -> None:
        self.store.save(self.settings)

    def update(self, **changes) -> Settings:
        for key, value in changes.items():
            setattr(self.settings, key, value)
        self.persist()
        return self.settings

    def resolve_geometry(self) -> WindowGeometry:
        screen = get_screen_size()
        geometry = self.settings.window_geometry if self.settings.remember_window_geometry else None
        return sanitize_geometry(geometry or default_overlay_geometry(screen), screen)

    def set_geometry(self, width: int, height: int, left: int, top: int) -> None:
        self.settings.window_geometry = WindowGeometry(width=width, height=height, left=left, top=top)
        if self.settings.remember_window_geometry:
            self.persist()

    def reset_geometry(self) -> WindowGeometry:
        geometry = default_overlay_geometry(get_screen_size())
        self.settings.window_geometry = geometry
        self.persist()
        return geometry

