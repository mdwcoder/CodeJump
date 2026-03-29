from __future__ import annotations

import flet as ft


BG = "#06070A"
PANEL = "#0E1015"
CARD = "#14171E"
CARD_ACTIVE = "#1A2330"
CARD_BORDER = "#232937"
ACCENT = "#58C8F2"
ACCENT_SOFT = "#1F3B47"
TEXT = "#E6E9EF"
MUTED = "#8791A5"
SUCCESS = "#81D4A1"
WARNING = "#E3B567"
ERROR = "#F57B7B"


TYPE_COLORS = {
    "file": ("#183A47", "#5AD0F5"),
    "folder": ("#2F3D25", "#AAD879"),
    "symbol": ("#3C2A4C", "#E2A8FF"),
}


def apply_page_theme(page: ft.Page) -> None:
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG
    page.padding = 0
    page.spacing = 0
    page.window.bgcolor = BG
    page.theme = ft.Theme(color_scheme_seed=ACCENT, use_material3=True)


def panel_style() -> dict:
    return {
        "bgcolor": PANEL,
        "border_radius": 18,
        "border": ft.border.all(1, CARD_BORDER),
    }
