from __future__ import annotations

import flet as ft

from codejump.app.ui import theme
from codejump.core.models import SearchResult


def _item_label(item_type: str) -> tuple[str, str]:
    background, foreground = theme.TYPE_COLORS[item_type]
    return background, foreground


class ResultsList(ft.Container):
    def __init__(self, on_select, on_open) -> None:
        self.on_select = on_select
        self.on_open = on_open
        self.list_view = ft.ListView(
            expand=True,
            spacing=8,
            padding=ft.padding.symmetric(horizontal=0, vertical=0),
        )
        super().__init__(
            expand=True,
            padding=ft.padding.only(left=18, top=0, right=10, bottom=16),
            content=self.list_view,
        )

    def render(self, results: list[SearchResult], selected_index: int) -> None:
        self.list_view.controls.clear()
        if not results:
            self.list_view.controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=18, vertical=24),
                    bgcolor=theme.CARD,
                    border=ft.border.all(1, theme.CARD_BORDER),
                    border_radius=16,
                    content=ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text("No results yet", size=14, weight=ft.FontWeight.W_600, color=theme.TEXT),
                            ft.Text(
                                "Index the current project or refine the query to surface matching files, folders and symbols.",
                                size=11,
                                color=theme.MUTED,
                            ),
                        ],
                    ),
                )
            )
            return
        for index, result in enumerate(results):
            self.list_view.controls.append(self._build_row(index, result, selected_index == index))

    def _build_row(self, index: int, result: SearchResult, selected: bool) -> ft.Control:
        item = result.item
        badge_bg, badge_fg = _item_label(item.item_type.value)
        return ft.Container(
            bgcolor=theme.CARD_ACTIVE if selected else theme.CARD,
            border=ft.border.all(1, theme.ACCENT if selected else theme.CARD_BORDER),
            border_radius=16,
            ink=True,
            padding=ft.padding.symmetric(horizontal=14, vertical=12),
            on_click=lambda e, idx=index: self.on_select(idx),
            on_long_press=lambda e, idx=index: self.on_open(idx),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        alignment=ft.alignment.Alignment(0, 0),
                        border_radius=10,
                        bgcolor=badge_bg,
                        content=ft.Text(item.item_type.value[:1].upper(), color=badge_fg, size=12, weight=ft.FontWeight.W_700),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=3,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(item.display_name, size=14, weight=ft.FontWeight.W_600, color=theme.TEXT, expand=True),
                                    ft.Container(
                                        bgcolor="#18202B",
                                        border_radius=999,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        content=ft.Text(item.item_type.value.upper(), size=9, color=theme.ACCENT),
                                    ),
                                ]
                            ),
                            ft.Text(item.relative_path, size=11, color=theme.MUTED, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(
                                result.explanation.summary() or item.preview or "Ready to open",
                                size=11,
                                color="#A9B4C6",
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ],
                spacing=12,
            ),
        )
