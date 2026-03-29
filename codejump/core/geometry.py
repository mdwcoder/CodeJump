from __future__ import annotations

from codejump.core.models import WindowGeometry
from codejump.utils.platform_helpers import ScreenSize, is_macos
from codejump.utils.validators import clamp


MIN_WIDTH = 360
MIN_HEIGHT = 520
DEFAULT_WIDTH = 392
DEFAULT_HEIGHT = 840
SCREEN_MARGIN = 24


def default_overlay_geometry(screen: ScreenSize) -> WindowGeometry:
    width = min(DEFAULT_WIDTH, max(MIN_WIDTH, screen.width - 120))
    height = min(DEFAULT_HEIGHT, max(MIN_HEIGHT, screen.height - 80))
    top = max(SCREEN_MARGIN, (screen.height - height) // 2)
    if is_macos():
        left = max(SCREEN_MARGIN, screen.width - width - SCREEN_MARGIN)
    else:
        left = SCREEN_MARGIN
    return WindowGeometry(width=width, height=height, left=left, top=top)


def sanitize_geometry(geometry: WindowGeometry | None, screen: ScreenSize) -> WindowGeometry:
    if geometry is None:
        return default_overlay_geometry(screen)
    width = clamp(int(geometry.width), MIN_WIDTH, max(MIN_WIDTH, screen.width - 40))
    height = clamp(int(geometry.height), MIN_HEIGHT, max(MIN_HEIGHT, screen.height - 40))
    max_left = max(SCREEN_MARGIN, screen.width - width - SCREEN_MARGIN)
    max_top = max(SCREEN_MARGIN, screen.height - height - SCREEN_MARGIN)
    left = clamp(int(geometry.left), 0, max_left)
    top = clamp(int(geometry.top), 0, max_top)
    return WindowGeometry(width=width, height=height, left=left, top=top)
