from __future__ import annotations

import flet as ft

from codejump.app.ui import theme


class SearchBar(ft.Container):
    def __init__(self, on_change) -> None:
        self.input = ft.TextField(
            border_radius=14,
            border_color="#1F2836",
            focused_border_color=theme.ACCENT,
            cursor_color=theme.ACCENT,
            hint_text="Search by intent…",
            hint_style=ft.TextStyle(color="#667085"),
            text_size=16,
            color=theme.TEXT,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=16),
            autofocus=True,
            on_change=on_change,
        )
        super().__init__(
            padding=ft.padding.only(left=18, top=0, right=18, bottom=14),
            content=ft.Stack(
                controls=[
                    self.input,
                    ft.Container(
                        alignment=ft.alignment.Alignment(1, 0),
                        padding=ft.padding.only(right=14),
                        content=ft.Text("Enter", size=10, color=theme.MUTED),
                    ),
                ]
            ),
        )
